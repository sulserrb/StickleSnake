configfile: "resources/configs/model_params.yaml" #We need to specify the config file that contains the parameters for the script

if not config.get("included_by_parent", False): #set "all" rule when run independently, but not when running the whole pipeline
    DATA_DIR = config.get("data_dir", "data")
    rule all:
        input:
            f"{DATA_DIR}/output/fold_summary_table.tex" #We need to specify the number of folds for cross-validation


#Adjust for zero based indexing
FOLDS = range(1, int(config["folds"]) + 1)

#Build paths for ease of use
INPUT_TPS = f"{DATA_DIR}/{config['input_tps']}"
INPUT_DIR = f"{DATA_DIR}/{config['input_folder']}"

rule crop_lands: 
    input: 
        lands = INPUT_TPS, #We need to specify the input tps file that contains the landmark coordinates
        directory = INPUT_DIR, #We need to specify the directory that contains the cropped images, which will be used to match the landmark coordinates with the corresponding images
    output: 
        f"{DATA_DIR}/landmarks/cropped_input.tps"
    log: 
        notebook="logs/crop_lands.log"
    benchmark:
        "benchmarks/bench_crop_lands.txt"
    shell: 
        "python3 scripts/crop_tps_coordinates.py "
        "{input.lands} " 
        "{output} "
        "{input.directory} "
        "> {log.notebook} 2>&1"

rule generate_folds: 
    input:
        directory = f"{DATA_DIR}/cropped_images/",
        lands = f"{DATA_DIR}/landmarks/cropped_input.tps"
    params:
        kfolds = config["folds"] #We need to specify the number of folds for cross-validation
    output:
        expand([f"{DATA_DIR}/output/fold{{fold}}/test.txt",
                f"{DATA_DIR}/output/fold{{fold}}/train.txt"], 
                fold=FOLDS)
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log:
        notebook="logs/generate_folds.log" #log file path
    benchmark:
        "benchmarks/bench_generate_folds.txt"
    shell:
        "python3 scripts/ml-morph_scripts/Kfold.py "
        "-i {input.directory} "
        f"-o {DATA_DIR}/output/ "
        "-k {params.kfolds} "

rule preprocess_landmark_model: 
    input: 
        directory = INPUT_DIR,
        lands = f"{DATA_DIR}/landmarks/cropped_input.tps",
        fold_files = [f"{DATA_DIR}/output/fold{{fold}}/test.txt", f"{DATA_DIR}/output/fold{{fold}}/train.txt"]
    output: 
        f"{DATA_DIR}/output/fold{{fold}}/train.xml",
        f"{DATA_DIR}/output/fold{{fold}}/test.xml",
        temp(directory(f"{DATA_DIR}/output/fold{{fold}}/test/")),
        temp(directory(f"{DATA_DIR}/output/fold{{fold}}/train/"))
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log: 
        notebook="logs/preprocess_landmark_model_{fold}.log" #log file path
    benchmark:
        "benchmarks/bench_preprocess_landmark_model_{fold}.txt"
    shell:
        "python3 scripts/ml-morph_scripts/preprocessing.py "
        "-i {input.directory} "
        "-t {input.lands} "
        "-k True "
        "-f {wildcards.fold} "
        "-o {DATA_DIR}/output/ "
        "> {log.notebook} 2>&1"

rule train_landmark_models: 
    input: 
        test = f"{DATA_DIR}/output/fold{{fold}}/test.xml",
        train = f"{DATA_DIR}/output/fold{{fold}}/train.xml",
        test_dir = f"{DATA_DIR}/output/fold{{fold}}/test/",
        train_dir = f"{DATA_DIR}/output/fold{{fold}}/train/"
    output: 
        model = "models/landmark_model_{fold}.dat",
        metrics = "models/landmark_model_{fold}_metrics.csv"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log:
        notebook="logs/train_landmark_model_{fold}.log" #log file path
    benchmark:
        "benchmarks/bench_train_landmark_model_{fold}.txt"
    shell:
        "python3 scripts/ml-morph_scripts/shape_trainer.py "
        "-d {input.train} "
        "-t {input.test} "
        "-th {config[threads]} "
        "-dp {config[tree_depth]} "
        "-c {config[cascade_depth]} "
        "-nu {config[nu_reg_param]} "
        "-os {config[oversampling]} "
        "-f {config[feature_size]} "
        "-n {config[num_trees]} "
        "-s {config[test_splits]} "
        "-o {output.model} "
        "> {log.notebook} 2>&1"
#Coming soon: a rule to evaluate and automatically select best model based on metrics. 

rule predict_landmarks_multifolds:
    input:
        directory= INPUT_DIR,
        model = "models/landmark_model_{fold}.dat",
    output:
        xml = f"{DATA_DIR}/output/predicted_landmarks_fold_{{fold}}.xml",
        tps =f"{DATA_DIR}/output/predicted_landmarks_fold_{{fold}}.tps"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/predict_landmarks_fold_{fold}.log" #log file path
    benchmark:
        "benchmarks/bench_predict_landmarks_fold_{fold}.txt"
    shell:
        "python3 scripts/ml-morph_scripts/prediction.py "
        "-i {input.directory} "
        "-p {input.model} "
        "-o {output.xml} "
        "> {log.notebook} 2>&1"


rule evaluate_landmark_predictions:
    input:
        predicted = f"{DATA_DIR}/output/predicted_landmarks_fold_{{fold}}.tps",
        true = f"{DATA_DIR}/landmarks/cropped_input.tps"
    output:
        f"{DATA_DIR}/output/landmark_distances_fold_{{fold}}.csv"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/evaluate_landmark_predictions_fold_{fold}.log" #log file path
    benchmark:
        "benchmarks/bench_evaluate_landmark_predictions_fold_{fold}.txt"
    shell:
        "python3 scripts/calculate_distances_tps.py "
        "--file_a {input.predicted} "
        "--file_b {input.true} "
        "--output_file {output} "
        "> {log.notebook} 2>&1"

rule visualize_landmark_predictions:
    input:
        land_data = f"{DATA_DIR}/output/landmark_distances_fold_{{fold}}.csv",
    output:
        f"{DATA_DIR}/output/results_table_fold_{{fold}}.tex"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/visualize_landmark_predictions_fold_{fold}.log" #log file path
    benchmark:
        "benchmarks/bench_visualize_landmark_predictions_fold_{fold}.txt"
    shell:
        "python3 scripts/analyze_distances.py "
        "--input_csv {input.land_data} "
        "--all_visualizations "
        "--fold {wildcards.fold} "
        "--output_dir {DATA_DIR}/output "
        "> {log.notebook} 2>&1"

rule summarize_folds:
    input:
        expand("models/landmark_model_{fold}_metrics.csv", fold=FOLDS), 
        expand(f"{DATA_DIR}/output/results_table_fold_{{fold}}.tex", fold=FOLDS), 
    output:
        f"{DATA_DIR}/output/fold_summary_table.tex"
    conda: 
        "envs/metrics_env.yaml" #We need to specify the conda env
    log:
        notebook="logs/summarize_folds.log" #log file path
    benchmark:
        "benchmarks/bench_summarize_folds.txt"
    shell:
        "python3 scripts/summarize_folds.py "
        "--input_files {input} "
        "--output_file {output} "
        "> {log.notebook} 2>&1"