for i in 'Capped(MELD)_DynaMELD_MELD3.0_None' 'Capped(MELD)_DynaMELD_Biological_None' 'Capped(MELD)_DynaMELD_Common_None' 'Capped(MELD)_DynaMELD_MELD3.0_First' 'Capped(MELD)_DynaMELD_MELD3.0_First_Second' 'Capped(MELD)_DynaMELD_Biological_First' 'Capped(MELD)_DynaMELD_Biological_First_Second' 'Capped(MELD)_DynaMELD_Common_First' 'Capped(MELD)_DynaMELD_Common_First_Second' RAW_MELD RAW_MELDNa RAW_MELD3.0
do
    python simulate.py 5 1 $i
done