# PULLING DATA FROM OPTIMIZELY

Code for pulling project, experiment, stats, and variation data from Optimizely.

## SETUP

1. Clone repository
```shell
    git clone https://gitlab.com/uvaaland/optimizely.git
```

2. Setup Conda environment
```shell
    conda create -n optimizely python=3
    conda activate optimizely
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
A log of the run can be found in the 'YYYY-MM-DD.log' file corresponding to the date of the run.
