from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine(supported_languages = ["en", "es", "it", "pl"]) # Need to allow additional languages to remove unsupported entities
anonymizer = AnonymizerEngine()

# Get list of all entities able to identify
pii_masking_list = analyzer.get_supported_entities()

# List of entities to avoid masking 
exempt_list = ["URL", # Don't need to anonymize websites
               "NRP", # Could be useful to pull user's race in some cases i.e. feeling alienated and alone
               "LOCATION", # Passing city/state into LLM isn't specific enough to identify users
               "IT_VAT_CODE", "IT_DRIVER_LICENSE", "IT_PASSPORT", "IT_FISCAL_CODE", "IT_IDENTITY_CARD", # Creates error message if not removed (Don't have Italian language setup)
               "ES_NIE", "ES_NIF", # Creates error message if not removed (Don't have Spanish language setup)
               "PL_PESEL", # Creates error message if not removed (Don't have Polish language setup) 
               ]
pii_masking_list = [i for i in pii_masking_list if i not in exempt_list]

def anonymize_pii(text): 
    results = analyzer.analyze(text=text,
                                entities=pii_masking_list,
                                language="en")
    anonymized_text = anonymizer.anonymize(text = text, analyzer_results = results)
    return anonymized_text.text
