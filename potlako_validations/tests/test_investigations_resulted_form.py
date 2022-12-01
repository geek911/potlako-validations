from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import OTHER

from ..form_validators import InvestigationsResultedFormValidator
from .models import SubjectConsent, SubjectVisit, Appointment
from .models import PathologyTestType


@tag('tr')
class TestInvestigationsResultedForm(TestCase):

    def setUp(self):
        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111', consent_datetime=get_utcnow(),
            gender='M', dob=(get_utcnow() - relativedelta(years=25)).date())
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000')
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment)

    def test_diagnoses_made_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'non-malignant',
            'diagnoses_made': None
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnoses_made', form_validator._errors)

    def test_diagnoses_results_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'malignant',
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('cancer_type', form_validator._errors)

    def test_diagnoses_results_other_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': OTHER,
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnosis_results_other', form_validator._errors)

    def test_diagnoses_results_valid(self):
        PathologyTestType.objects.create(name=OTHER,
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'malignant',
            'cancer_type': 'blah'
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_diagnoses_inconclusive_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'inconclusive',
            'diagnoses_made': 'blah'
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnoses_made', form_validator._errors)

    def test_diagnoses_untraceable_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'untraceable',
            'diagnoses_made': 'blah'
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnoses_made', form_validator._errors)

    def test_diagnoses_suggestive_invalid(self):
        PathologyTestType.objects.create(name='pah',
                                         short_name=OTHER)
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'diagnosis_results': 'suggestive',
            'diagnoses_made': 'blah'
        }
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnoses_made', form_validator._errors)
        
    @tag('dm')
    def test_malignant_diagnosis_made_required(self):
        cleaned_data = {
            'subject_visit': self.subject_visit,
            'tests_resulted_type_other': None,
            'imaging_tests': None,
            'pathology_received_date': None,
            'pathology_communicated_date': None,
            'imaging_tests_date': None,
            'diagnosis_results': 'inconclusive',
            'diagnosis_results_other': None,
            'pathology_result_date': None,
            'cancer_type': None,
            'diagnoses_made': None,
            'results_reviewed': None
            
        }
        
        form_validator = InvestigationsResultedFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('diagnoses_made', form_validator._errors)
        
    
