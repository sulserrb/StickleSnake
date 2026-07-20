if not config.get("included_by_parent", False): #set "all" rule when run independently, but not when running the whole pipeline
    rule all:
        input:
            "data/output/predicted_landmarks_scaled.tps" #Run to retrieve scaled landmarks for all specimens

configfile: "resources/configs/landmarking_params.yaml"

rule predict_landmarks:
    input:
        directory= "data/cropped_images/",
        model = config["model_path"] #We need to specify the path to the trained model that will be used for prediction,
    output:
        "data/output/predicted_landmarks.tps"
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
        "-o {output} "
        "> {log.notebook} 2>&1"

rule apply_scales_to_landmarks:
    input:
        predicted = "data/output/predicted_landmarks.tps",
        scales = "data/measurements/specimen_scales.csv"
    output:
        "data/output/predicted_landmarks_scaled.tps"
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
