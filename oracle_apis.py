import cx_Oracle
import pandas as pd
import calendar
import base64
from driver_helper import clear_crap as cc


def ipd_patient_details(m):
    admission_details = [
        {
            'complain': u'',
            'admission_ID': u'',
            'admission_date': u'',
            'speciality': False,
            'doctor_ID': False,
            'doctor_name': u''
        }
    ]

    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    # lis = list()
    mr = m
    mr = "'" + mr + "'"
    query = "SELECT initcap(cn.pc) pc, a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant from ADMISSION.TBL_ADMISSION A, emr.const_notes         CN, doctors                 d, specialities            sp WHERE a.pk_str_admission_id = cn.id_ and a.fk_int_admitting_dr_id = d.doctor_id and d.primary_speciality_id = sp.speciality_id and a.mr# = " + mr + " and cn.pc is not null group by initcap(cn.pc), a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant"
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['complain', 'admission_ID', 'admission_date', 'speciality',
                                      'doctor_ID', 'doctor_name'], )
        print(df)
        # d = str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[:-6]

        query_result = {
            'complain': df.iloc[0][0],
            'admission_ID': df.iloc[1][0],
            'admission_date': df.iloc[2][0],
            'speciality': df.iloc[3][0],
            'doctor_ID': df.iloc[4][0],
            'doctor_name': df.iloc[5][0]
        }
        admission_details.append(query_result)
    admission_details.pop(0)
    print(admission_details)
    print(len(admission_details))
    if len(admission_details) > 0:
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def ipd_patient_details_with_date(date, m):
    month = date[3:5]
    month = int(month)
    nu = calendar.month_name[month]
    date = str(date[0:3]) + str(nu) + "/" + str(date[-4:])
    print(month)
    query = "SELECT initcap(cn.pc) pc, a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant from ADMISSION.TBL_ADMISSION A, emr.const_notes         CN, doctors                 d, specialities            sp WHERE a.pk_str_admission_id = cn.id_ and a.fk_int_admitting_dr_id = d.doctor_id and d.primary_speciality_id = sp.speciality_id and a.mr# = '" + m + "' and cn.pc is not null and trunc(a.fld_dat_adm_date)='" + date + "' group by initcap(cn.pc), a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant"
    print(query)
    admission_details = [
        {
            'complain': u'',
            'admission_ID': u'',
            'admission_date': u'',
            'speciality': False,
            'doctor_ID': False,
            'doctor_name': u''
        }
    ]

    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    # lis = list()
    mr = m
    mr = "'" + mr + "'"
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['complain', 'admission_ID', 'admission_date', 'speciality',
                                      'doctor_ID', 'doctor_name'], )
        print(df)
        # d = str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[:-6]

        query_result = {
            'complain': df.iloc[0][0],
            'admission_ID': df.iloc[1][0],
            'admission_date': df.iloc[2][0],
            'speciality': df.iloc[3][0],
            'doctor_ID': df.iloc[4][0],
            'doctor_name': df.iloc[5][0]
        }
        admission_details.append(query_result)
    admission_details.pop(0)
    print(admission_details)
    print(len(admission_details))
    if len(admission_details) > 0:
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def ipd_patient_details_dates_only(m):
    admission_details = [
        {
            'admission_ID': u'',
            'admission_date': u'',
        }
    ]

    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    # lis = list()
    mr = m
    mr = "'" + mr + "'"
    query = "SELECT initcap(cn.pc) pc, a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant from ADMISSION.TBL_ADMISSION A, emr.const_notes         CN, doctors                 d, specialities            sp WHERE a.pk_str_admission_id = cn.id_ and a.fk_int_admitting_dr_id = d.doctor_id and d.primary_speciality_id = sp.speciality_id and a.mr# = " + mr + " and cn.pc is not null group by initcap(cn.pc), a.pk_str_admission_id, a.fld_dat_adm_date, sp.speciality_name, d.doctor_id, d.consultant"
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['complain', 'admission_ID', 'admission_date', 'speciality',
                                      'doctor_ID', 'doctor_name'], )
        # print(df)
        # d = str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[2][0]), format="%D/%M/%Y"))[:-9])[:-6]
        query_result = {
            'admission_ID': df.iloc[1][0],
            'admission_date': df.iloc[2][0]
        }
        admission_details.append(query_result)
    admission_details.pop(0)
    print(admission_details)
    print(len(admission_details))
    if len(admission_details) > 0:
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details(m):
    visit_details = [
        {
            'visit_id': u'',
            'visit_date': u'',
            'speciality': u'',
            'doctor_ID': u'',
            'doctor_name': u''
        }
    ]
    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    mr = m
    mr = "'" + mr + "'"
    query = "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant from cashglobal_details_opd p, cashglobal_opd         o, specialities           sp, doctors                d where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id  and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' and o.mr# = " + mr + " and o.site_id = '1'"
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['visit_id', 'visit_date', 'speciality', 'doctor_ID',
                                      'doctor_name'], )
        print(df)
        # d = str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[1][0]), format="%m/%d/%y"))[:-9])[:-6]
        query_result = {
            'visit_id': df.iloc[0][0],
            'visit_date': df.iloc[1][0],
            'speciality': df.iloc[2][0],
            'doctor_ID': df.iloc[3][0],
            'doctor_name': df.iloc[4][0]
        }
        visit_details.append(query_result)
    visit_details.pop(0)
    print(visit_details)
    print(len(visit_details))
    if len(visit_details) > 0:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details_dates_only(m):
    visit_details = [
        {
            'visit_id': u'',
            'visit_date': u'',
        }
    ]
    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    mr = m
    mr = "'" + mr + "'"
    query = "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant from cashglobal_details_opd p, cashglobal_opd         o, specialities           sp, doctors                d where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id  and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' and o.mr# = " + mr + " and o.site_id = '1'"
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['visit_id', 'visit_date', 'speciality', 'doctor_ID',
                                      'doctor_name'], )
        print(df)
        # d = str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[1][0]), format="%m/%d/%y"))[:-9])[:-6]
        query_result = {
            'visit_id': df.iloc[0][0],
            'visit_date': df.iloc[1][0],
        }
        visit_details.append(query_result)
    visit_details.pop(0)
    print(visit_details)
    print(len(visit_details))
    if len(visit_details) > 0:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details_with_date(date, m):
    mr = m
    mr = "'" + mr + "'"
    month = date[3:5]
    month = int(month)
    nu = calendar.month_name[month]
    date = str(date[0:3]) + str(nu) + "/" + str(date[-4:])
    print(date)
    print(month)
    query = "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant from cashglobal_details_opd p, cashglobal_opd         o, specialities           sp, doctors                d where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id  and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' and o.mr# =" + mr + "and o.site_id = '1' and trunc(o.tran_date) = '" + date + "'"
    print(query)
    visit_details = [
        {
            'visit_id': u'',
            'visit_date': u'',
            'speciality': u'',
            'doctor_id': u'',
            'doctor_name': u''
        }
    ]
    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['visit_id', 'visit_date', 'doctor_speciality',
                                      'doctor_id', 'doctor_name'], )
        print(df)
        # d = str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9]
        # dd = d[5:7]
        # d = (str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
        #     (df.iloc[1][0]), format="%m/%d/%y"))[:-9])[:-6]
        #print(d)
        query_result = {
            'visit_id': df.iloc[0][0],
            'visit_date': df.iloc[1][0],
            'doctor_speciality': df.iloc[2][0],
            'doctor_id': df.iloc[3][0],
            'doctor_name': df.iloc[4][0]
        }
        visit_details.append(query_result)
    visit_details.pop(0)
    print(visit_details)
    print(len(visit_details))
    if len(visit_details) > 0:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def demo(m):
    query_result = {}
    mr = m
    mr = "'" + mr + "'"
    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    ca = cursor
    query = "select p.mr#,p.cell_phone#,p.patient_full_name,p.patient_gender,e.ADDRESS,e.AGE,e.DOB,e.province_state from patients p,ODS.EMR_PATIENT_DEMOGRAPHICS e where p.mr#=e.mr# and e.mr#= " + mr
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['MR#', 'CELL_PHONE#', 'PATIENT_FULL_NAME',
                                      'PATIENT_GENDER', 'ADDRESS', 'AGE', 'DOB', 'PROVINCE_STATE'], )
        a = "select c.name from registration.patients p left join tbl_cm_sub_company sc on p.fk_str_sub_panel_id = sc.sub_code left join tbl_cm_company c on sc.code = c.code where p.mr# = " + mr
        print(df)
        for roww in ca.execute(a):
            d = pd.DataFrame(roww, index=['PANEL', ], )
        query_result = {
            'mr#': df.iloc[0][0],
            'cell_number': df.iloc[1][0],
            'patient_full_name': df.iloc[2][0],
            'patient_gender': df.iloc[3][0],
            'address': df.iloc[4][0],
            'age': str(df.iloc[5][0]).split()[0],
            'dob': str(df.iloc[6][0])[:-9],
            'province_state': df.iloc[7][0],
            'panel_name': d.iloc[0][0]
        }
    return query_result


def mrd_emp_data():
    emp_details = []
    bs64 = str()
    query = "select t.emp_id || '.jpg' ,t.name,p.photo, t.email from employee_list_working t,employee_profile p where t.dept_id=19 and t.emp_id=p.emp_id"
    dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')
    cursor = dsn_tns.cursor()
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=['EMP_ID', 'NAME', 'PHOTO', 'EMAIL'], )
        print(df)
        f = open("temp/" + str(df.iloc[0][0]), 'wb')
        f.write(df.iloc[2][0])
        f.close()
        # now we will get the base 64 of the image here
        with open("temp/" + df.iloc[0][0], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            bs64 = encoded_string
            tp = {
                'emp_id': (df.iloc[0][0]).replace(".jpg", ''),
                'name': df.iloc[1][0],
                'base64': bs64.decode("utf-8"),
                'department': "MEDICAL RECORDS",
                'email': df.iloc[3][0]
            }
            emp_details.append(tp)

    cc('temp')
    print(emp_details)
    res = {
            "data": emp_details,
            "status": True,
            "statusCode": 200,
            "message": "Success",
            "error": ""
    }
    return res


if __name__ == '__main__':
    mrd_emp_data()
