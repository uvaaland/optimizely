# OPTIMIZELY API FOR M4A

Code for pulling Optimizely data for M4A.

## SETUP

1. Clone repository
```shell
    git clone https://gitlab.com/uvaaland/optimizely.git
```

2. Setup Conda environment
```shell
    conda create -n m4a python=3
    source activate m4a
```

3. Install requirements
```shell
    cd optimizely/
    make init
```

4. Run tests
```shell
    make test
```
NOTE: No tests are currently implemented and this step will fail.

## PROVIDE TOKEN FILE

1. Create a folder for the token
```shell
    mkdir token/
```

2. Put Optimizely token in token.txt file
```shell
    echo [OPTIMIZELY TOKEN] > token/token.txt
```

## PULL OPTIMIZELY DATA

1. If there is no output folder, create this before pulling the data
```shell
    mkdir output/
```

2. Once the token has been set up, we can pull the project, experiment, stats
   and variation data
```shell
    make pull
```

3. Once the procedure has finished, the data can be found as .csv files in the output/ folder.

