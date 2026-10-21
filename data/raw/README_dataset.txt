ISMAILIA SEWAGE TREATMENT PLANT (ISTP) — OPERATIONAL MONITORING DATASET, 2000–2008
================================================================================

ASSOCIATED ARTICLE
  "Interpretable Machine Learning and Rolling-Origin Validation Identify Two
  Distinct Control and Predictability Regimes in Full-Scale Aerated Lagoon
  Performance"
  Journal of Environmental Management (manuscript JEMA-D-26-09646).

CONTENTS
  Ismailia_WWTP_monitoring_2000-2008.csv    Monitoring dataset (UTF-8, comma-separated)
  Ismailia_WWTP_monitoring_2000-2008.xlsx   Same data + a "Data dictionary" sheet
  README_dataset.txt                        This file

DESCRIPTION
  Daily operational monitoring record of the ISTP full-scale aerated-lagoon
  sewage-treatment plant (Serabioum, ~12 km SSW of Ismailia City, Egypt;
  30.486 N, 32.247 E; design capacity 90,000 m3/d). The record covers
  2000-01-01 to 2008-12-31. It contains 8,211 rows = 2,737 sampling dates x 3
  in-series lagoon stages (aerated, facultative, maturation). There are NO
  missing values. For each date, the eight influent/operational columns are
  identical across the three stage-rows (they describe the common plant inlet),
  while the six effluent columns give the quality measured at the outlet of the
  stage indicated by the "Stage" column.

 

COLUMN DICTIONARY  (column | description | units)
  SampleDate     Calendar date of the monitoring record                 | YYYY-MM-DD
  Year           Calendar year (derived)                                | year
  DateSerial     Original numeric date code, model input X10            | day
                 (Excel 1900 system; 36526 = 2000-01-01)
  WeekDay        Day-of-week code (1-7)                                  | -
  Stage          Treatment-stage index (1,2,3) = aerated, facultative,  | -
                 maturation lagoon at whose outlet the effluent sample
                 was taken (influent columns repeat across the 3 stages)
  BOD5_inf       Influent 5-day biochemical oxygen demand               | mg/L
  TSS_inf        Influent total suspended solids                        | mg/L
  Coliform_inf   Influent fecal coliform                                | MPN/100 mL
  Temp           Recorded water/operational temperature (model input X4)| degC
  Flow           Influent flow rate (plant inlet)                       | m3/d
  pH_inf         Influent pH                                            | pH units
  VSS_inf        Influent volatile suspended solids                     | mg/L
  DO_inf         Influent dissolved oxygen                              | mg/L
  BOD5_eff       Effluent BOD5 at the indicated stage                   | mg/L
  TSS_eff        Effluent total suspended solids at the indicated stage | mg/L
  Coliform_eff   Effluent fecal coliform at the indicated stage         | MPN/100 mL
  pH_eff         Effluent pH at the indicated stage                     | pH units
  VSS_eff        Effluent volatile suspended solids at the indicated stage | mg/L
  DO_eff         Effluent dissolved oxygen at the indicated stage       | mg/L

MISSING VALUES
  None. All 8,211 records are complete for every column.

DATA SHOWN IN THE ARTICLE (Table 1)
  Influent flow            90,652 m3/d   
  Effluent BOD5            71.0 mg/L
  Effluent TSS             88.8 mg/L
  Effluent fecal coliform  4.6 x 10^4 MPN/100 mL
  Influent fecal coliform  1.82 x 10^7 MPN/100 mL
  Temperature              22.5 degC
  

DATA SOURCE / PROVENANCE
  Operational monitoring records of the ISTP aerated-lagoon plant, Serabioum,
  Ismailia Governorate, Egypt.
 

LICENSE
  Creative Commons Attribution 4.0 International (CC BY 4.0) 


CONTACT
  Corresponding author of the associated article.
