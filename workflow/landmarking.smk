configfile: "resources/configs/landmarking_params.yaml"

if not config.get("included_by_parent", False):
     #set "all" rule when run independently, but not when running the whole pipeline
     #set local variable for data directory
    DATA_DIR = config.get("data_dir", "data")
    rule all:
        input:
            f"{DATA_DIR}/output/predicted_landmarks_scaled.tps" #Run to retrieve scaled landmarks for all specimens


rule predict_landmarks:
    input:
        directory= (f"{DATA_DIR}/cropped_images"),
        model = config["model_path"] #We need to specify the path to the trained model that will be used for prediction,
    output:
        tps = f"{DATA_DIR}/output/predicted_landmarks.tps",
        xml = f"{DATA_DIR}/output/predicted_landmarks.xml"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/predict_landmarks.log" #log file path
    benchmark:
        "benchmarks/bench_predict_landmarks.txt"
    shell:
        "python3 scripts/ml-morph_scripts/prediction.py "
        "-i {input.directory} "
        "-p {input.model} "
        "-o {output.xml} "
        "> {log.notebook} 2>&1"

rule apply_scales_to_landmarks:
    input:
        predicted = (f"{DATA_DIR}/output/predicted_landmarks.tps"),
        scales = (f"{DATA_DIR}/measurements/specimen_scales.csv")
    output:
        f"{DATA_DIR}/output/predicted_landmarks_scaled.tps"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/apply_scales_to_landmarks.log" #log file path
    benchmark:
        "benchmarks/bench_apply_scales_to_landmarks.txt"
    shell:
        "python3 scripts/Apply_Scale_To_TPS.py "
        "--tps {input.predicted} "
        "--csv {input.scales} "
        "--out {output} "
        "--invert-scale "
        "> {log.notebook} 2>&1"
