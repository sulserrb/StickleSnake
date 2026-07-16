configfile: "resources/configs/model_params.yaml" #We need to specify the config file that contains the parameters for the script

if not config.get("run_all"): #set "all" rule when run independently, but not when running the whole pipeline
    rule all:
        input:
            "data/output/results_table.tex" #We need to specify the number of folds for cross-validation

rule crop_lands: 
    input: 
        lands =config["input_tps"], #We need to specify the input tps file that contains the landmark coordinates
        directory = config["input_folder"], #We need to specify the directory that contains the cropped images, which will be used to match the landmark coordinates with the corresponding images
    output: 
        "data/landmarks/cropped_input.tps"
    log: 
        notebook="logs/crop_lands.log"
    benchmark:
        "benchmarks/bench_crop_lands.txt"
    shell: 
        "python3 scripts/crop_tps_coordinates.py "
        "{input.lands} " 
        "{output} "
        "{input.directory}"
        "> {log.notebook} 2>&1"

rule generate_folds: 
    input:
        directory = "data/cropped_images/",
        lands = "data/landmarks/cropped_input.tps"
    params:
        kfolds = config["folds"] #We need to specify the number of folds for cross-validation
    output:
        expand(["data/output/fold{fold}/test.txt",
                "data/output/fold{fold}/train.txt"], 
                fold=range(config["folds"]))
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log:
        notebook="logs/generate_folds.log" #log file path
    benchmark:
        "benchmarks/bench_generate_folds.txt"
    shell:
        "python3 scripts/ml-morph_scripts/Kfold.py "
        "-i {input.directory} "
        "-o data/output/"
        "-k {params.kfolds} "

rule preprocess_landmark_model: 
    input: 
        directory = config["input_folder"],
        lands = "data/landmarks/cropped_input.tps",
        fold_dir = "data/output/fold{fold}",
        fold_files = ["data/output/fold{fold}/test.txt", "data/output/fold{fold}/train.txt"]
    output: 
        "data/output/fold{fold}/train.xml",
        "data/output/fold{fold}/test.xml",
        temp(directory("data/output/fold{fold}/test/")),
        temp(directory("data/output/fold{fold}/train/"))
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
        "> {log.notebook} 2>&1"

rule train_landmark_models: 
    input: 
        test = "data/output/fold{fold}/test.xml",
        train = "data/output/fold{fold}/train.xml",
        test_dir = "data/output/fold{fold}/test/",
        train_dir = "data/output/fold{fold}/train/"
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
#Add rule comparing and choose best model for future use - unfinished! 

rule predict_landmarks_multifolds:
    input:
        directory= config["input_folder"],
        model = "models/landmark_model_{fold}.dat",
    output:
        "data/output/predicted_landmarks_fold_{fold}.tps"
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
        "-o {output} "
        "> {log.notebook} 2>&1"


rule evaluate_landmark_predictions:
    input:
        predicted = "data/output/predicted_landmarks_fold_{fold}.tps",
        true = "data/landmarks/cropped_input.tps"
    output:
        "data/output/landmark_distances_fold_{fold}.csv"
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
        land_data = "data/output/landmark_distances_fold_{fold}.csv",
    output:
        "data/output/results_table_fold_{fold}.tex"
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
        "> {log.notebook} 2>&1"

rule summarize_folds:
    input:
        expand("models/landmark_model_{fold}_metrics.csv", fold=range(config["folds"]))
    output:
        "data/output/fold_summary_table.tex"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/summarize_folds.log" #log file path
    benchmark:
        "benchmarks/bench_summarize_folds.txt"
    shell:
        "python3 scripts/summarize_folds.py "
        "--input_files {input} "
        "--output_file {output} "
        "> {log.notebook} 2>&1"