from Param_TKA import *
from Libraries_TKA import *

def main():

    # todo: enrollees.txt ::
    enrollees = pd.read_csv(descript_base_dir + "Enrollees.txt", sep="|")
    enrollee_col = ["ID", "P02HISP", "P02RACE", "P02SEX", "V00CHRTHLF", "V00COHORT", "V00IMAGESC", "V00IMAGESE"]
    enrollees= enrollees[enrollee_col]
    print("enrollees .unique().shape:", enrollees['ID'].unique().shape)

    # todo: AllClinical.txt :: womac pain scores
    # todo: ['V00WOMKPR', 'V00WOMKPL', 'V01WOMKPR', 'V01WOMKPL', 'V03WOMKPR', 'V03WOMKPL', 'V05WOMKPR', 'V05WOMKPL', 'V06WOMKPR', 'V06WOMKPL']
    allclinical_pain_col = [] #
    for visit in [0,1,3,5,6]:# 0,1,3,5,6,8,10 # 0-> base, 1->12m, 3->24m, 5->36, 6->48
        visit_str = "{0:0=2d}".format(visit)
        womac00 = pd.read_csv(descript_base_dir + "AllClinical"+visit_str+".txt",sep="|")
        needed = ["V" + visit_str + "WOMKPR", "V" + visit_str + "WOMKPL"] # V00WOMKPR & V00WOMKPL
        womac00 = womac00[["ID"] + needed]
        print("WOMKP "+visit_str+" .unique().shape:", womac00["ID"].unique().shape )

        allclinical_pain_col.extend(needed)
        enrollees = enrollees.merge(womac00, suffixes=('', '_duplicate'), on='ID', how='left')

    # todo: Outcomes99.txt
    outcomes99 = pd.read_csv(descript_base_dir + "Outcomes99"  + ".txt", sep="|")
    dict ={"id":"ID"}
    outcomes99.rename(columns=dict,inplace=True)
    outcomes99 = outcomes99[["ID", "V99ELKBLRP", "V99ERKBLRP",    # left knee, knee replacement seen on baseline OAI x-ray (calc)
                             "V99ELKDAYS", "V99ERKDAYS",    # days between enrollment visit and follow-up knee replacement
                             "V99ELKLOA", "V99ERKLOA", # V99ELKLOA Num 8 VISIT. Outcomes: left knee, last visit with OA (KLG>=2) (calc)
                             "V99ELXNOA","V99ERXNOA", # V99ELXNOA Num 8 VISIT. Outcomes: left knee, last visit KL < 2 (calc)
                             "V99ELKVSAF", "V99ERKVSAF"]]# V99ELKVSAF Num 8 VISIT. Outcomes: left knee, closest OAI contact after follow-up knee replacement (calc)
    print("outcomes99 .unique().shape:", outcomes99['ID'].unique().shape)
    enrollees = enrollees.merge(outcomes99, suffixes=('', '_duplicate'), on='ID', how='left')

    # todo: BMI:: Clinical_FNIH.txt !!!!!!!!!!!!!!
    # todo: ONLY 600 patient !!!
    Clinical_FNIH = pd.read_csv(descript_base_dir + "Clinical_FNIH" + ".txt", sep="|")
    Clinical_FNIH = Clinical_FNIH[["ID", "P01BMI"]]
    print("Clinical_FNIH .unique().shape:",  Clinical_FNIH['ID'].unique().shape)
    # enrollees = enrollees.merge(Clinical_FNIH, suffixes=('', '_duplicate'), on='ID', how='left')

    # todo: age:: SubjectChar00.txt
    SubjectChar00 = pd.read_csv(descript_base_dir + "SubjectChar00" + ".txt", sep="|")
    SubjectChar00 = SubjectChar00[["ID", "V00AGE"]]
    print("SubjectChar00 unique patients:", SubjectChar00['ID'].unique().shape)
    # enrollees = enrollees.merge(SubjectChar00, suffixes=('', '_duplicate'), on='ID', how='left')

    # todo: age:: MeasInventory.csv
    MeasInventory = pd.read_csv(descript_base_dir + "MeasInventory" + ".csv", sep=",")
    dict ={"id":"ID"}
    MeasInventory.rename(columns=dict,inplace=True)
    MeasInventory = MeasInventory[["ID", "V00AGE","V00XRKLR","V00XRKLL"]] #  V00XRKLL Num 8 LADDER. Baseline KL Grade Left
    print("MeasInventory .unique().shape:", MeasInventory['ID'].unique().shape)
    enrollees = enrollees.merge(MeasInventory, suffixes=('', '_duplicate'), on='ID', how='left')

    # todo: MRI00.txt

    # todo: Duplicates :: if any
    duplicate = [x for x in enrollees.columns if "_duplicate" in x]
    print("Duplicated columns after join:", duplicate)



    # TODO: Filtering Criterias
    print("\nFiltering Criterias")
    enrollees = enrollees.replace('.: Missing Form/Incomplete Workbook', np.nan)
    print( ((enrollees.isna().sum()).to_frame()).T)
    # progression and incident Cohort
    enrollees = enrollees[enrollees["V00COHORT"] != '3: Non-exposed control group']
    print("Cohorts:", enrollees.V00COHORT.unique().T,enrollees.shape)
    # : (1) age, gender, race, and ***BMI*** at baseline;
    enrollees.dropna(subset=["V00AGE", "P02SEX", "P02RACE", "P02HISP"], how='any', inplace=True)
    print("demo:", enrollees['ID'].unique().shape)
    # (2) grade of knee OA at baseline
    enrollees.dropna(subset=["V00XRKLR","V00XRKLL"], how='any', inplace=True)
    print("KL grade:", enrollees['ID'].unique().shape)
    # womac normilized to 0 to 100
    right_joint= [x for x in allclinical_pain_col if "WOMKPR" in x]
    left_joint = [x for x in allclinical_pain_col if "WOMKPL" in x]
    # enrollees.dropna(subset=allclinical_pain_col, how='any', inplace=True) # 3784 -> 1347
    enrollees = enrollees[  ~ (enrollees[right_joint].isna().any(axis=1) &  enrollees[left_joint].isna().any(axis=1))   ] # 3795 -> 1354
    print("WOMKP: ", enrollees['ID'].unique().shape)
    # print("min womkp:", enrollees[allclinical_pain_col].min().to_frame().T)
    # print("max womkp:", enrollees[allclinical_pain_col].max().to_frame().T)
    for x in allclinical_pain_col:
        enrollees[x] = enrollees[x] * 5
    # •	TKR in either knee at baseline # "V99ELKBLRP", "V99ERKBLRP"
    enrollees = enrollees[enrollees["V99ELKBLRP"]!="1: Yes"]
    enrollees = enrollees[enrollees["V99ERKBLRP"] != "1: Yes"]
    print("TKA-baseline: ", enrollees['ID'].unique().shape)



    # todo: presistent pain progression: 9+ point increase betweeen baseline and two or more follow-up time in first 48 month

    print("\nright_joint order:", right_joint)
    print("left_joint order:", left_joint)
    enrollees['right_joint_is_monotonic'] = enrollees[right_joint].apply(lambda x: x.is_monotonic, axis=1)
    enrollees['left_joint_is_monotonic'] = enrollees[left_joint].apply(lambda x: x.is_monotonic, axis=1)
    def difference_func(row):
        a=row.values
        b=row.values
        a=a[0] # [:(len(a)-1)]
        b=b[1:]
        sub_ba = np.subtract(b, a)
        sub_ba = np.asarray(sub_ba)
        count_9 = (sub_ba >= 9).sum()
        return((count_9>=2))
    enrollees['right_joint_2_jump'] = enrollees[right_joint].apply(lambda row: difference_func(row), axis=1)
    enrollees['left_joint_2_jump'] = enrollees[left_joint].apply(lambda row: difference_func(row), axis=1)
    enrollees["left_eligible"] = (enrollees["left_joint_2_jump"] ) #& enrollees["left_joint_is_monotonic"])
    enrollees["right_eligible"] = (enrollees["right_joint_2_jump"] ) #& enrollees["right_joint_is_monotonic"])
    case= enrollees[  ( enrollees["left_eligible"] | enrollees["right_eligible"] )]
    print("Pain 9+>=2 eligible: ",case.shape)
    print("Pain Eligible:", case["left_eligible"].sum(), case["right_eligible"].sum(),(case["left_eligible"].sum() + case["right_eligible"].sum()))
    # print(case.head(),"\n", case[case["left_eligible"]][left_joint].head(),"\n", case[case["right_eligible"]][right_joint].head())

    # def difference_func(row):
    #     a=row.values
    #     b=row.values
    #     a=a[0] # [:(len(a)-1)]
    #     b=b[1:]
    #     sub_ba = np.subtract(b, a)
    #     sub_ba = np.asarray(sub_ba)
    #     count_9 = (sub_ba == 0).sum()
    #     return((count_9==4))
    # enrollees['right_Not_eligible'] = enrollees[right_joint].apply(lambda row: difference_func(row), axis=1)
    # enrollees['left_Not_eligible'] = enrollees[left_joint].apply(lambda row: difference_func(row), axis=1)
    enrollees['right_control'] = (enrollees[right_joint]==0).all(axis=1)
    enrollees['left_control'] = (enrollees[left_joint]==0).all(axis=1)

    control = enrollees[(enrollees["right_control"] | enrollees["left_control"])]
    print("\nNot 5-<=2 control: ", control.shape)
    print("control:", control["left_control"].sum(), control["right_control"].sum(),(control["left_control"].sum() + control["right_control"].sum()))
    print(control.head(), "\n", control[control["left_control"]][left_joint].head(), "\n",control[control["right_control"]][right_joint].head())

    # •	Excluded if partial knee replacement, TKR at baseline, not matched,
    # •	Matched on age, BMI, sex, ethnicity (baseline confounding var.)
    enrollees.to_csv( "enrollees" + ".csv", index=True)


if __name__ == '__main__':
    main()