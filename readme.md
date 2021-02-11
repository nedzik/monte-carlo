# A simple Monte-Carlo forecaster

A simple Monte-Carlo forecaster that takes an Excel file as an input.
Please, note, that many features are still under development. 


## How to install

We have tested the script on Linux (Ubuntu 18.04), running Python 3.6.9. 
It may or may not work on Windows or other operating systems. 

We recommend that you create a Python 3 virtual environment. Once you have the environment 
created and activated, install the dependencies:

```bash
pip install -r requrements.txt
```

# Help

The script takes one required argument, the name of an Excel file. 
The script supports a number of options. To learn what they are, run:

```bash
./forecaster --help
```

We are still working on properly documenting all the options; please, bear with us.


## Input

The script tries to read the Excel document specified as its argument. 
If your Excel file contains multiple worksheets, you can use ```-s``` or ```--sheet-name``` 
to specify the sheet the script should read. 

The script looks at two columns for forecasting: lower and upper bounds. 
Please, put your 90% confidence interval or CI (or whatever you prefer) in these two columns. 
You can override column names by specifying ```-l``` or ```--lower-bound-column``` and ```-u``` or 
```--upper-bound-column``` respectively. 

The script removes all rows that do not meet the condition of the value 
in lower column being less than the value in upper column. You can use this trick to
exclude certain rows from forecasting.

The script uses ```-c``` or ```--experiment-count``` to run a number of experiments,
then publish one or more CI of the outcome that these experiments have produced. 

The script uses a distribution function, provided explicitly or implicitly, 
to pick a random value from the CI defined by lower and upper bounds. 
Please, look at ```-d``` or ```-distribution-function``` for more details.

We will use a simple Excel file, ```examples/services.xlsx``` to illustrate
two different ways of running the script. 

## How to Run

Run a simulation against the whole file:

```bash
./forecast.py examples/services.xlsx
```
```text
95% CI - [9.18, 14.80] days
90% CI - [9.65, 14.35] days
80% CI - [9.93, 14.05] days
```

```bash
./forecast.py examples/services.xlsx -v
```
```text
./forecast.py examples/services.xlsx -v
20:53:52 — INFO — Reading examples/services.xlsx, sheet 'default' ...
20:53:52 — INFO — Read 5 rows.
20:53:52 — INFO — Removing rows where 'Upper' value is not greater than 'Lower' value ...
20:53:52 — INFO — Retained 5 rows.
20:53:52 — INFO — Trimming the dataset to 'Lower' and 'Upper' columns ...
20:53:52 — INFO — Removing rows with NaN values in the 'Lower' and 'Upper' columns ...
20:53:52 — INFO — Retained 5 rows.
20:53:52 — INFO — Using normal distribution function for value selection ...
20:53:52 — INFO — Running 10000 experiments ...
  [####################################]  100%          
95% CI - [9.21, 14.74] days
90% CI - [9.65, 14.31] days
80% CI - [9.93, 14.02] days
20:54:08 — INFO — Done.
```

Run a series of simulations using unique values in the column to split the problem into pieces:

```bash
./forecast.py examples/services.xlsx -t Category
```
```text
95% Confidence Intervals (in days):
Category,Lower,Upper
JSON,3.33,7.65
XML,4.69,8.30
```


