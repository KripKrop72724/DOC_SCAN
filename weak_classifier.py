import pytesseract
import glob
from PIL import Image

a = "HISTORY &"
aa = "PHYSICAL EXAMINATION"
b = "PROCEDURE CHECKLIST"
c = "Mandibular"
d = "Maxillary"
e = "REFUSES to be marked"
f = "CHECK-IN"
g = "SIGN OUT"
h = "Any equipment problems to be"
i = "GRAPHICAL ASSESSMENT"
j = "BSR"
k = "Pain Score"
l = "PEWS"
m = "INITIAL NURSING ASSESSMENT"
n = "Adult Early Warning Scores"
o = "SPO2 Oxygen Saturation"
p = "History of Present Illness :"
q = "Patient Medical Record"
r = "Personal Information Chart"
s = "Extremities & Blood Vessels"
t = "Signature Of Medical Officer :"
u = "Signature Of Attending Physician :"
v = "PHYSICIAN'S PROGRESS RECORD"
w = "Physician's Progress Record"
x = "PATIENT REGISTRATION FORM"
prf = "How Did You Hear About Us"
xx = "PHYSICIANS PROGRESS RECORD"
xx1 = "Progress Record"
xxx = "PROGRESS RECORD"
y = "The patient have(has) read this authorization"
z = "Name of Person/ Organization?"
a1 = "Modified Glasgow Coma Scale"
a2 = "CRY"
a3 = "ARMS"
a4 = "LEGS"
a5 = "ALERTNESS"
a6 = "Best verbal response"
a7 = "Best motor"
a77 = "patient is intubated"
a8 = "NEUROLOGICAL ASSESSMENT"
a9 = "CRV"
a10 = "Head Injury"
a11 = "Seizures"
a12 = "AUTHORIZATION AND CONSENT FOR"
a13 = "Treatment may include physical examination, diagnostic"
a14 = "I agree that if I (Patient) do not visit the hospital for treatment"
aut = "I fully understand that I will be the contact person"
aut1 = "Graduate Trainee Doctors under supervision"
a15 = "TREATMENT IN HOSPITAL"
qw = "FACE SHEET"
q1 = "PERMANENT ADDRESS"
q2 = "EMERGENCY CONTACT"
q3 = "TEMPORARY ADDRESS"
q4 = "NURSES NOTES"
q5 = "NURSE'S NOTES"
q6 = "Nurses Notes"
q7 = "Nurse's Notes"
q8 = "RIGHTS AND RESPONSIBILITIES"
q9 = "You shall receive care in a safe and secure environment"
q10 = "You shall be involved in aspects of medical care including"
q11 = "You shall be notified in case your attending physician requires"
q12 = "Nursing Assessment"
q13 = "Interpreter required"
q14 = "Cuddled"
q15 = "Have you had any unintentional weight hain or loss in"
q16 = "Have there been any recent changes in your ability to care for yourself"
gc = "GRAPHIC CHART"
gc1 = "AEWS"
gc2 = "O2"
gc3 = "Glucose"
gc4 = "Check"
gc5 = "Nurse"
ina = "INITIAL NURSING ASSESSMENT"
ina1 = "RECEIVING NOTES"
ina2 = "RESPS per minute"
ina3 = "Repeat AEWS SCORE"
td = "TRIAGE DOCUMENT"
td1 = "EMERGENCY DEPARTMENT"
td2 = "EMERGENCY SEVERITY"
td3 = "INDEX (ESI)"
td4 = "SCREENING TOOL"
nass = "NEUROLOGICAL ASSESSMENT"
nass1 = "Mild Weakness"
nass2 = "Spastic Flexion"
nass3 = "Record the response"
nass4 = "Closed by Swelling"
poo = "PHYSICIAN'S ORDERS"
poo1 = "PHYSICIANS ORDERS"
poo2 = "Physicians Orders"
poo3 = "Physician's Orders"
poo4 = "All intravenous orders"
poo5 = "Renewal orders"
peds = "Pediatric Early Warning Score"
peds1 = "Normal Vital Signs"
peds2 = "Age of Pediatric Patient"
peds3 = "Newborn"


def classify(image_path):
    for filename in glob.glob(image_path):
        check = pytesseract.image_to_string(Image.open(filename), lang='eng')
        print("Checking " + filename)
        if b in check:
            return 'BED SIDE PROCEDURE'
        elif c in check:
            return 'BED SIDE PROCEDURE'
        elif d in check:
            return 'BED SIDE PROCEDURE'
        elif e in check:
            return 'BED SIDE PROCEDURE'
        elif f in check:
            return 'BED SIDE PROCEDURE'
        elif g in check:
            return 'BED SIDE PROCEDURE'
        elif td in check:
            return 'TRIAGE DOCUMENT'
        elif td1 in check:
            return 'TRIAGE DOCUMENT'
        elif td2 in check:
            return 'TRIAGE DOCUMENT'
        elif td3 in check:
            return 'TRIAGE DOCUMENT'
        elif td4 in check:
            return 'TRIAGE DOCUMENT'
        elif poo in check:
            return "PHYSICIAN'S ORDERS"
        elif poo1 in check:
            return "PHYSICIAN'S ORDERS"
        elif poo2 in check:
            return "PHYSICIAN'S ORDERS"
        elif poo3 in check:
            return "PHYSICIAN'S ORDERS"
        elif poo4 in check:
            return "PHYSICIAN'S ORDERS"
        elif poo5 in check:
            return "PHYSICIAN'S ORDERS"
        elif peds in check:
            return "Pediatric Early Warning Score"
        elif peds1 in check:
            return "Pediatric Early Warning Score"
        elif peds2 in check:
            return "Pediatric Early Warning Score"
        elif peds3 in check:
            return "Pediatric Early Warning Score"
        elif nass in check:
            return 'NEUROLOGICAL ASSESSMENT'
        elif nass1 in check:
            return 'NEUROLOGICAL ASSESSMENT'
        elif nass2 in check:
            return 'NEUROLOGICAL ASSESSMENT'
        elif nass3 in check:
            return 'NEUROLOGICAL ASSESSMENT'
        elif nass4 in check:
            return 'NEUROLOGICAL ASSESSMENT'
        elif ina in check:
            return 'INITIAL NURSING ASSESSMENT'
        elif ina1 in check:
            return 'INITIAL NURSING ASSESSMENT'
        elif ina2 in check:
            return 'INITIAL NURSING ASSESSMENT'
        elif ina3 in check:
            return 'INITIAL NURSING ASSESSMENT'
        elif i in check:
            return 'GRAPHICAL ASSESSMENT'
        elif j in check:
            return 'GRAPHICAL ASSESSMENT'
        elif k in check:
            return 'GRAPHICAL ASSESSMENT'
        elif gc in check:
            return 'GRAPHIC CHART'
        elif (gc1 and gc2) in check:
            return 'GRAPHIC CHART'
        elif (gc3 and gc4 and gc5) in check:
            return 'GRAPHIC CHART'
        elif aa in check:
            return 'HISTORY AND PHYSICAL'
        elif a in check:
            return 'HISTORY AND PHYSICAL'
        elif p in check:
            return 'HISTORY AND PHYSICAL'
        elif s in check:
            return 'HISTORY AND PHYSICAL'
        elif t in check:
            return 'HISTORY AND PHYSICAL'
        elif u in check:
            return 'HISTORY AND PHYSICAL'
        elif q in check:
            return 'OLD FACE SHEET'
        elif r in check:
            return 'OLD FACE SHEET'
        elif xxx in check:
            return 'PHYSICIAN PROGRESS RECORD'
        elif xx1 in check:
            return 'PHYSICIAN PROGRESS RECORD'
        elif v in check:
            return 'PHYSICIAN PROGRESS RECORD'
        elif w in check:
            return 'PHYSICIAN PROGRESS RECORD'
        elif xx in check:
            return 'PHYSICIAN PROGRESS RECORD'
        elif x in check:
            return 'PATIENT REGISTRATION FORM'
        elif y in check:
            return 'PATIENT REGISTRATION FORM'
        elif z in check:
            return 'PATIENT REGISTRATION FORM'
        elif prf in check:
            return 'PATIENT REGISTRATION FORM'
        elif a1 in check:
            return 'MODIFIED GLASGOW COMA SCALE'
        elif (a2 and a3 and a4 and a5) in check:
            return 'MODIFIED GLASGOW COMA SCALE'
        elif (a6 and a7) in check:
            return 'MODIFIED GLASGOW COMA SCALE'
        elif a77 in check:
            return 'MODIFIED GLASGOW COMA SCALE'
        elif a8 in check:
            return 'HISTORY AND PHYSICAL'
        elif a9 in check:
            return 'HISTORY AND PHYSICAL'
        elif (a10 and a11) in check:
            return 'HISTORY AND PHYSICAL'
        elif a12 in check:
            return 'CONSENT FORM'
        elif a13 in check:
            return 'CONSENT FORM'
        elif a14 in check:
            return 'CONSENT FORM'
        elif a15 in check:
            return 'CONSENT FORM'
        elif aut in check:
            return 'CONSENT FORM'
        elif aut1 in check:
            return 'CONSENT FORM'
        elif qw in check:
            return 'FACE SHEET'
        elif q1 in check:
            return 'FACE SHEET'
        elif q2 in check:
            return 'FACE SHEET'
        elif q3 in check:
            return 'FACE SHEET'
        elif q4 in check:
            return 'NURSES NOTES'
        elif q5 in check:
            return 'NURSES NOTES'
        elif q6 in check:
            return 'NURSES NOTES'
        elif q7 in check:
            return 'NURSES NOTES'
        elif q8 in check:
            return 'PATIENT AND FAMILY RIGHTS'
        elif q9 in check:
            return 'PATIENT AND FAMILY RIGHTS'
        elif q10 in check:
            return 'PATIENT AND FAMILY RIGHTS'
        elif q11 in check:
            return 'PATIENT AND FAMILY RIGHTS'
        elif q12 in check:
            return 'NURSING ASSESSMENT'
        elif q13 in check:
            return 'NURSING ASSESSMENT'
        elif q14 in check:
            return 'NURSING ASSESSMENT'
        elif q15 in check:
            return 'NURSING ASSESSMENT'
        elif q16 in check:
            return 'NURSING ASSESSMENT'
        else:
            return None


def give_classes_data():
    classes_obj = {
        "EMERGENCY": [{"id": "XXQ01", "name": "BED SIDE PROCEDURE"},
                      {"id": "XXQ02", "name": "MODIFIED GLASGOW COMA SCALE"},
                      {"id": "XXQ03", "name": "INITIAL NURSING ASSESSMENT"}, {"id": "XXQ04", "name": "PEWS"},
                      {"id": "XXQ05", "name": "GRAPHICAL ASSESSMENT"}, {"id": "XXQ06", "name": "GRAPHICAL CHART"},
                      {"id": "XXQ07", "name": "NEUROLOGICAL ASSESSMENT"}, {"id": "XXQ08", "name": "TRIAGE DOCUMENT"}],
        "PATIENT CONSENT AND REGISTRATION INFORMATION": [{"id": "XXQ09", "name": "AUTHORIZATION AND CONSENT FORM"},
                                                         {"id": "XXQ10", "name": "FACE SHEET"},
                                                         {"id": "XXQ11", "name": "PATIENT MEDICAL RECORD"},
                                                         {"id": "XXQ12", "name": "PATIENT REGISTRATION FORM"}],
        "PATIENT HISTORY": [{"id": "XXQ13", "name": "HISTORY AND PHYSICAL"},
                            {"id": "XXQ14", "name": "NURSING ASSESSMENT"}, {"id": "XXQ15", "name": "PHYSICIANS ORDERS"},
                            {"id": "XXQ16", "name": "PHYSICIAN PROGRESS RECORD"}]
    }
    return classes_obj
