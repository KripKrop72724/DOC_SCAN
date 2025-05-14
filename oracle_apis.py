import os
import shutil

import cx_Oracle
import pandas as pd
import calendar
import base64
from driver_helper import clear_crap as cc
from MONGO_CRED import dsn_tns


def ipd_patient_details(m):
    cursor = dsn_tns.cursor()

    query = """
    SELECT initcap(cn.pc) AS complain, 
           a.pk_str_admission_id AS admission_ID, 
           a.fld_dat_adm_date AS admission_date, 
           sp.speciality_name AS speciality, 
           d.doctor_id AS doctor_ID, 
           d.consultant AS doctor_name
    FROM ADMISSION.TBL_ADMISSION A, 
         emr.const_notes CN, 
         doctors d, 
         specialities sp 
    WHERE a.pk_str_admission_id = cn.id_ 
      AND a.fk_int_admitting_dr_id = d.doctor_id 
      AND d.primary_speciality_id = sp.speciality_id 
      AND a.mr# = :mr 
      AND cn.pc IS NOT NULL 
    GROUP BY initcap(cn.pc), 
             a.pk_str_admission_id, 
             a.fld_dat_adm_date, 
             sp.speciality_name, 
             d.doctor_id, 
             d.consultant 
    ORDER BY TO_DATE(a.fld_dat_adm_date, 'DD/MM/YYYY') DESC
    """

    cursor.execute(query, mr=m)

    admission_details = []
    for row in cursor:
        query_result = {
            'complain': row[0],
            'admission_ID': row[1],
            'admission_date': row[2],
            'speciality': row[3],
            'doctor_ID': row[4],
            'doctor_name': row[5]
        }
        admission_details.append(query_result)

    if admission_details:
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def check_mortality(mr):
    """
    Checks if the given MR number exists in the admission.mortality table.
    Returns True if found, otherwise False.
    """
    cursor = dsn_tns.cursor()
    # Prepare the MR value for the SQL query
    mr_str = "'" + mr + "'"
    query = "SELECT COUNT(*) FROM admission.mortality WHERE MR# = " + mr_str
    cursor.execute(query)
    result = cursor.fetchone()
    # If the count is greater than zero, the MR exists in the mortality table.
    if result and result[0] > 0:
        return True
    else:
        return False


def ipd_patient_details_with_date(date, m):

    month = int(date[3:5])
    nu = calendar.month_abbr[month].upper()  # abbreviated month in upper case
    date_formatted = str(date[0:3]) + nu + "/" + str(date[-4:])
    print("DEBUG: Reformatted date:", date_formatted)

    query = """
    SELECT complain,
           pk_str_admission_id,
           fld_dat_adm_date,
           speciality_name,
           doctor_id,
           consultant
    FROM (
      SELECT initcap(cn.pc) AS complain,
             adm.pk_str_admission_id,
             adm.fld_dat_adm_date,
             sp.speciality_name,
             d.doctor_id,
             d.consultant,
             ROW_NUMBER() OVER (PARTITION BY adm.pk_str_admission_id ORDER BY cn.pc) AS rn
      FROM ADMISSION.TBL_ADMISSION adm
      LEFT JOIN emr.const_notes cn
             ON adm.pk_str_admission_id = cn.id_
      LEFT JOIN doctors d
             ON adm.fk_int_admitting_dr_id = d.doctor_id
      LEFT JOIN specialities sp
             ON d.primary_speciality_id = sp.speciality_id
      WHERE adm.mr# = '{m}'
        AND trunc(adm.fld_dat_adm_date) = TO_DATE('{dte}', 'DD-MON-YYYY')
    )
    WHERE rn = 1
    """.format(m=m, dte=date_formatted)

    print("DEBUG: Executing query:")
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

    cursor = dsn_tns.cursor()

    for row in cursor.execute(query):
        df = pd.DataFrame([row], columns=['complain', 'admission_ID', 'admission_date',
                                          'speciality', 'doctor_ID', 'doctor_name'])
        print("DEBUG: DataFrame row:")
        print(df)
        query_result = {
            'complain': df['complain'].iloc[0],
            'admission_ID': df['admission_ID'].iloc[0],
            'admission_date': df['admission_date'].iloc[0],
            'speciality': df['speciality'].iloc[0],
            'doctor_ID': df['doctor_ID'].iloc[0],
            'doctor_name': df['doctor_name'].iloc[0]
        }
        admission_details.append(query_result)

    admission_details.pop(0)

    print("DEBUG: Final admission_details:")
    print(admission_details)
    print("DEBUG: Number of rows fetched:", len(admission_details))

    if len(admission_details) > 0:
        admission_details.sort(key=lambda x: x['admission_ID'])
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def ipd_patient_details_dates_only(m):
    admission_details = []
    cursor = dsn_tns.cursor()
    mr = "'" + m + "'"
    query = """
    SELECT DISTINCT adm.pk_str_admission_id, 
                    adm.fld_dat_adm_date
    FROM ADMISSION.TBL_ADMISSION adm
    LEFT JOIN emr.const_notes cn ON adm.pk_str_admission_id = cn.id_
    LEFT JOIN doctors d ON adm.fk_int_admitting_dr_id = d.doctor_id
    LEFT JOIN specialities sp ON d.primary_speciality_id = sp.speciality_id
    WHERE adm.mr# = {}
    ORDER BY TO_DATE(adm.fld_dat_adm_date, 'DD/MM/YYYY') DESC
    """.format(mr)

    for row in cursor.execute(query):
        query_result = {
            'admission_ID': row[0],
            'admission_date': row[1]
        }
        admission_details.append(query_result)

    print(admission_details)
    print(len(admission_details))

    if admission_details:
        return admission_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def ipd_patient_details_without_complain(m):
    admission_details = []

    try:
        cursor = dsn_tns.cursor()

        mr = "'" + m + "'"

        query = """
        SELECT 
            MAX(initcap(cn.pc)) AS complain, 
            adm.pk_str_admission_id AS admission_ID, 
            adm.fld_dat_adm_date AS admission_date, 
            MAX(sp.speciality_name) AS speciality, 
            MAX(d.doctor_id) AS doctor_ID, 
            MAX(d.consultant) AS doctor_name
        FROM ADMISSION.TBL_ADMISSION adm
        LEFT JOIN emr.const_notes cn 
               ON adm.pk_str_admission_id = cn.id_
        LEFT JOIN doctors d 
               ON adm.fk_int_admitting_dr_id = d.doctor_id
        LEFT JOIN specialities sp 
               ON d.primary_speciality_id = sp.speciality_id
        WHERE adm.mr# = {}
        GROUP BY adm.pk_str_admission_id, adm.fld_dat_adm_date
        ORDER BY TO_DATE(adm.fld_dat_adm_date, 'DD/MM/YYYY') DESC
        """.format(mr)

        print("DEBUG: Executing query:")
        print(query)

        for row in cursor.execute(query):
            print("DEBUG: Retrieved row:", row)
            query_result = {
                'complain': row[0] if row[0] is not None else '',
                'admission_ID': row[1],
                'admission_date': row[2],
                'speciality': row[3] if row[3] is not None else '',
                'doctor_ID': row[4] if row[4] is not None else '',
                'doctor_name': row[5] if row[5] is not None else ''
            }
            admission_details.append(query_result)

        print("DEBUG: Total rows fetched:", len(admission_details))

    except Exception as e:
        print("ERROR: Exception occurred while executing query")
        print("ERROR:", e)

    if admission_details:
        return admission_details
    else:
        print("DEBUG: No records found for MR:", m)
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details(m):
    # visit_details = [
    #     {
    #         'visit_id': u'',
    #         'visit_date': u'',
    #         'speciality': u'',
    #         'doctor_ID': u'',
    #         'doctor_name': u''
    #     }
    # ]
    # cursor = dsn_tns.cursor()
    # mr = m
    # mr = "'" + mr + "'"
    # query = (
    #         "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant "
    #         "from cashglobal_details_opd p, cashglobal_opd o, specialities sp, doctors d "
    #         "where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id "
    #         "and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' "
    #         "and o.mr# = " + mr + " and o.site_id = '1' "
    #                               "ORDER BY o.tran_date DESC"
    # )
    # print("DEBUG: Executing query:")
    # print(query)
    #
    # for row in cursor.execute(query):
    #     # Create a DataFrame for this row with labeled columns.
    #     df = pd.DataFrame([row], columns=['visit_id', 'visit_date', 'speciality', 'doctor_ID', 'doctor_name'])
    #     print("DEBUG: DataFrame row:")
    #     print(df)
    #     query_result = {
    #         'visit_id': df.iloc[0][0],
    #         'visit_date': df.iloc[0][1],
    #         'speciality': df.iloc[0][2],
    #         'doctor_ID': df.iloc[0][3],
    #         'doctor_name': df.iloc[0][4]
    #     }
    #     visit_details.append(query_result)
    # # Remove the initial template dictionary
    # visit_details.pop(0)
    # print("DEBUG: Final visit_details:")
    # print(visit_details)
    # print("DEBUG: Number of rows fetched:", len(visit_details))
    # if len(visit_details) > 0:
    #     return visit_details
    # else:
    #     return {"Error": "Either the record was not available or there was an error"}
    visit_details = [
        {
            'visit_id': u'',
            'visit_date': u'',
            'speciality': u'',
            'doctor_ID': u'',
            'doctor_name': u''
        }
    ]
    cursor = dsn_tns.cursor()
    mr = "'" + m + "'"

    query = (
            "SELECT t.visit_id, t.entry_date, sp.speciality_name, t.doctor_id, d.consultant "
            "FROM registration.const_notes t "
            "LEFT JOIN doctors d ON t.doctor_id = d.doctor_id "
            "LEFT JOIN specialities sp ON d.primary_speciality_id = sp.speciality_id "
            "WHERE t.isactive = 'Y' "
            "AND t.mr# = " + mr + " "
                                  "ORDER BY t.entry_date DESC"
    )

    print("DEBUG: Executing query:")
    print(query)

    for row in cursor.execute(query):
        df = pd.DataFrame([row], columns=['visit_id', 'visit_date', 'speciality', 'doctor_ID', 'doctor_name'])
        print("DEBUG: DataFrame row:")
        print(df)

        query_result = {
            'visit_id': df.iloc[0][0],
            'visit_date': df.iloc[0][1],
            'speciality': df.iloc[0][2],
            'doctor_ID': df.iloc[0][3],
            'doctor_name': df.iloc[0][4]
        }
        visit_details.append(query_result)

    visit_details.pop(0)

    print("DEBUG: Final visit_details:")
    print(visit_details)
    print("DEBUG: Number of rows fetched:", len(visit_details))

    if len(visit_details) > 0:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details_dates_only(m):
    # visit_details = [
    #     {
    #         'visit_id': u'',
    #         'visit_date': u'',
    #     }
    # ]
    # cursor = dsn_tns.cursor()
    # mr = m
    # mr = "'" + mr + "'"
    # query = "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant from cashglobal_details_opd p, cashglobal_opd         o, specialities           sp, doctors                d where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id  and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' and o.mr# = " + mr + " and o.site_id = '1'"
    # for row in cursor.execute(query):
    #     df = pd.DataFrame(row, index=['visit_id', 'visit_date', 'speciality', 'doctor_ID',
    #                                   'doctor_name'], )
    #     print(df)
    #     # d = str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9]
    #     # dd = d[5:7]
    #     # d = (str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
    #     #     (df.iloc[1][0]), format="%m/%d/%y"))[:-9])[:-6]
    #     query_result = {
    #         'visit_id': df.iloc[0][0],
    #         'visit_date': df.iloc[1][0],
    #     }
    #     visit_details.append(query_result)
    # visit_details.pop(0)
    # print(visit_details)
    # print(len(visit_details))
    # if len(visit_details) > 0:
    #     return visit_details
    # else:
    #     return {"Error": "Either the record was not available or there was an error"}
    visit_details = []
    cursor = dsn_tns.cursor()
    query = (
            "SELECT t.visit_id, t.entry_date, sp.speciality_name, t.doctor_id, d.consultant "
            "FROM registration.const_notes t "
            "LEFT JOIN doctors d ON t.doctor_id = d.doctor_id "
            "LEFT JOIN specialities sp ON d.primary_speciality_id = sp.speciality_id "
            "WHERE t.isactive = 'Y' "
            "AND t.mr# = '" + m + "' "
                                  "ORDER BY t.entry_date DESC"
    )

    for row in cursor.execute(query):
        print(row)
        visit_id, entry_date, speciality, doctor_id, consultant = row
        query_result = {
            'visit_id': visit_id,
            'visit_date': entry_date
        }
        visit_details.append(query_result)

    print(visit_details)
    print(len(visit_details))

    if visit_details:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def opd_patient_details_with_date(date, m):
    # mr = m
    # mr = "'" + mr + "'"
    # month = date[3:5]
    # month = int(month)
    # nu = calendar.month_name[month]
    # date = str(date[0:3]) + str(nu) + "/" + str(date[-4:])
    # print(date)
    # print(month)
    # query = "select o.tran_id, o.tran_date, sp.speciality_name, p.doctor_id, d.consultant from cashglobal_details_opd p, cashglobal_opd         o, specialities           sp, doctors                d where p.tran_id = o.tran_id and p.doctor_id = d.doctor_id  and d.primary_speciality_id = sp.speciality_id and p.major_id = '5555' and o.mr# =" + mr + "and o.site_id = '1' and trunc(o.tran_date) = '" + date + "'"
    # print(query)
    # visit_details = [
    #     {
    #         'visit_id': u'',
    #         'visit_date': u'',
    #         'speciality': u'',
    #         'doctor_id': u'',
    #         'doctor_name': u''
    #     }
    # ]
    # cursor = dsn_tns.cursor()
    # for row in cursor.execute(query):
    #     df = pd.DataFrame(row, index=['visit_id', 'visit_date', 'doctor_speciality',
    #                                   'doctor_id', 'doctor_name'], )
    #     print(df)
    #     # d = str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9]
    #     # dd = d[5:7]
    #     # d = (str(pd.to_datetime((df.iloc[1][0]), format="%D/%M/%Y"))[:-9])[-2:] + "/" + dd + "/" + (str(pd.to_datetime(
    #     #     (df.iloc[1][0]), format="%m/%d/%y"))[:-9])[:-6]
    #     #print(d)
    #     query_result = {
    #         'visit_id': df.iloc[0][0],
    #         'visit_date': df.iloc[1][0],
    #         'doctor_speciality': df.iloc[2][0],
    #         'doctor_id': df.iloc[3][0],
    #         'doctor_name': df.iloc[4][0]
    #     }
    #     visit_details.append(query_result)
    # visit_details.pop(0)
    # print(visit_details)
    # print(len(visit_details))
    # if len(visit_details) > 0:
    #     return visit_details
    # else:
    #     return {"Error": "Either the record was not available or there was an error"}
    mr = "'" + m + "'"
    month = date[3:5]
    month = int(month)
    nu = calendar.month_name[month]
    date = str(date[0:3]) + str(nu) + "/" + str(date[-4:])
    print(date)
    print(month)
    query = (
            "SELECT t.visit_id, t.entry_date, sp.speciality_name, t.doctor_id, d.consultant "
            "FROM registration.const_notes t "
            "LEFT JOIN doctors d ON t.doctor_id = d.doctor_id "
            "LEFT JOIN specialities sp ON d.primary_speciality_id = sp.speciality_id "
            "WHERE t.isactive = 'Y' "
            "AND t.mr# = " + mr + " "
                                  "AND trunc(t.entry_date) = '" + date + "' "
                                                                         "ORDER BY t.entry_date DESC"
    )
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

    cursor = dsn_tns.cursor()
    for row in cursor.execute(query):
        df = pd.DataFrame([row], columns=['visit_id', 'visit_date', 'speciality', 'doctor_id', 'doctor_name'])
        print(df)
        query_result = {
            'visit_id': df.iloc[0]['visit_id'],
            'visit_date': df.iloc[0]['visit_date'],
            'speciality': df.iloc[0]['speciality'],
            'doctor_id': df.iloc[0]['doctor_id'],
            'doctor_name': df.iloc[0]['doctor_name']
        }
        visit_details.append(query_result)

    visit_details.pop(0)
    print(visit_details)
    print("Number of rows fetched:", len(visit_details))

    if visit_details:
        return visit_details
    else:
        return {"Error": "Either the record was not available or there was an error"}


def demo(m):
    query_result = {}
    mr = m
    mr = "'" + mr + "'"
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
    """
    Fetch employee details (ID, name, email, department) and their photos from Oracle DB,
    encode photos to base64, and return a structured response.
    Departments filtered: 19 (MEDICAL RECORDS), 45 (OPERATING ROOM).
    """
    emp_details = []
    temp_folder = "temp"

    try:
        # Create the temporary folder if it doesn't exist
        os.makedirs(temp_folder, exist_ok=True)

        # Query to select required fields and filter by departments
        query = """
            SELECT t.emp_id || '.jpg' AS filename,
                   t.name,
                   p.photo,
                   t.email,
                   t.dept_id
              FROM employee_list_working t
              JOIN employee_profile p ON t.emp_id = p.emp_id
             WHERE t.dept_id IN (19, 45)
        """

        cursor = dsn_tns.cursor()
        cursor.execute(query)

        for row in cursor:
            filename, name, photo, email, dept_id = row

            # Determine department name
            if dept_id == 19:
                department = "MEDICAL RECORDS"
            elif dept_id == 45:
                department = "OPERATING ROOM"
            else:
                department = "UNKNOWN"

            encoded_string = ""
            if photo:
                try:
                    # Write the photo to a file (for legacy compatibility)
                    file_path = os.path.join(temp_folder, filename)
                    with open(file_path, 'wb') as f:
                        f.write(photo)

                    # Encode directly from bytes to avoid extra I/O read
                    encoded_string = base64.b64encode(photo).decode('utf-8')
                except Exception as e:
                    print("Failed processing photo for %s: %s", filename, e)
            else:
                print("No photo data for %s. Skipping encoding.", filename)

            emp_details.append({
                'emp_id': filename.rsplit('.', 1)[0],
                'name': name,
                'base64': encoded_string,
                'department': department,
                'email': email
            })

    except Exception as e:
        print("Error in mrd_emp_data: %s", e)
    finally:
        # Clean up the temporary folder
        try:
            if os.path.isdir(temp_folder):
                shutil.rmtree(temp_folder)
        except Exception as e:
            print("Failed to remove temp folder '%s': %s", temp_folder, e)

    # Build the final response
    return {
        "data": emp_details,
        "status": True,
        "statusCode": 200,
        "message": "Success",
        "error": ""
    }


if __name__ == '__main__':
    opd_patient_details_dates_only('228897')
    print("===============================")
    opd_patient_details("228897")
    # opd_patient_details_with_date("")
