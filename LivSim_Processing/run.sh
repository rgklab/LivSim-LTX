for i in DynaMELD_MELD3.0_None DynaMELD_Biological_None DynaMELD_Common_None MELD MELDNa MELD3.0 ORACLE
do
    python simulate.py 5 1 $i
done