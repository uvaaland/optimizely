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
    make init
```

4. Run tests
```shell
    make test
```

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

1. Once the token has been set up, we can pull the project, experiment, stats
   and variation data
```shell
    make pull
```
The whole procedure takes ~2 minutes.

2. Once the procedure has finished, the data can be found as .csv files in the output/ folder.

