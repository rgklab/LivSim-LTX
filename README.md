# LivSim-Codes
LivSim is an extensible, open-source discrete-event simulation of the allocation of livers in the US Organ Procurement and Transplantation Network (OPTN).  The most recent version, LivSim 1.11, is written for Python 3.4.2 and  is designed to work in tandem with the Liver Simulated Allocation Model (LSAM) (v. Aug 2014) as a separate module. For more information, refer to the LivSim_Manual.pdf.

For example input files, please download from the following link:

https://www.dropbox.com/sh/xyayeut88dip5t5/AADDOS4aq8XFNcjgHwPzf6FFa?dl=0

Note that the input files are randomly generated from the actual LSAM input files to preserve medical privacy. 

Please cite the following papers if you use this code:
1. Kilambi, Vikram, and Sanjay Mehrotra. "Improving liver allocation using optimized neighborhoods." Transplantation 101.2 (2017): 350-359.
2. Mehrotra, Sanjay, et al. "A Concentric Neighborhood Solution to Disparity in Liver Access That Contains Current UNOS Districts." Transplantation 102.2 (2018): 255-278.
3. Kilambi, Vikram, Kevin Bui, and Sanjay Mehrotra. "LivSim: An Open-Source Simulation Software Platform for Community Research and Development for Liver Allocation Policies." Transplantation 102.2 (2018).

## Data processing part
This session provide a description on how to process SRTR data to run on Livsim.

### Change constants in `dataPreparation/config.py`
`OUTPUT_DIRECTORY`: The output directory that save SRTR generated files for Livsim input.

`MELD_POLICY`: The policy that meld score is calculated, choice between `regular`, `sodium`, `30`(MELD3.0), `deepsurv`.

`DATA_DIRECTORY`: The original raw SRTR data files.  

`INPUT_DIRECTORY`: The generated csv file from SRTR to use for data preparation. For sodium policy data, select directory of files generated from data preparation using sodium policy. etc.  

`SIMULATOR_START_TIME`: Start time of the simulation.

`SIMULATOR_END_TIME`: End time of the simulation
### Example execution:


### Step 1, load_sas()
It loads sas file of cand_liin.sas and stathist_linn_deepsurv.sas into csv files. Notice that the dynamic file (stathist_linn) file need a column called `deepsurv` which contains the MELD score from deepsurv model.
**Notice here that you need to change the file path to the current location**.

### Step 2, execute main()
Below explain the following sub steps in `main` function.
#### load_sample_csv()
Load the sample static and dynamic csv for removal files or original files. 
#### preprocessing_file()
This function aim to remove HCC diagnosis and Status 1 patients. save the removed result into two files, `stathist_liin_deepsurv_removal.csv` and `cand_linn_removal.csv`.
#### create_patient()
Create `SRTR_Patient.csv` and `SRTR_Waitlist_matchmeld.csv`. 
- `get_constraint_px()` need to change the file path that provide the the patient ids `srtr_val_split.txt` to provide constraint patient ids
**Need to change the file path**
#### create_status()
Create `SRTR_Status.csv`
#### Create Donor.csv file
- `load_raw_donor_sas(directory_path)` create `tx_li.csv` from `tx_li.sas`file. **Need to change the file path for sas**
-  load the `tx_li.csv`
- `create_donors(tx_li)` create `SRTR_Donors.csv`

## Run test case for data preparation
```angular2html
pytest dataPreparation/testing/
```

## Run the simulator
### Change Constants in `LivSim_Processing/config.py`
`REDUCED_MODEL`: set it to `True` to use reduced model (the supported version).

`INPUT_DIRECTORY`: the input files directory for Livsim Simulator. Example:`dataPreparation/preprocess_result_30`

`MODIFIED`:  set it to `True` to use the speed up version. `False` for the orginal version.
### Start the Simulator
```angular2html
~: cd LivSim_Processing
~: python simulate.py 5 1 [1,0,0,0] 35 15 5 "../output/"
```
For detail of what each of the arguments means, please refer to page 12 in LivSim manual.

## Post processing 
run `post_processing()` in `dataPreparation` directory. 

This is for counting the death in male and female before(`total_death_gender_count.csv`) and after (`DeepsurvSRTR_gender_count.csv`)the simulation running.


**Please change the `DeepsurvSRTR_RawOutput_IDdeaths.csv` to read from corresponded directory and change `SRTR_gender_count.csv` to the desired output directory.**













