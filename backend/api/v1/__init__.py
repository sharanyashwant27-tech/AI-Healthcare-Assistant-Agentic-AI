"""API v1 routers."""

from fastapi import APIRouter

from . import (
    advanced,
    apis,
    appointments,
    auth,
    chat,
    dashboard,
    database,
    doctors,
    embeddings,
    emergency,
    fhir,
    followup,
    graphrag,
    hitl,
    imaging,
    insurance,
    knowledge,
    lab,
    notifications,
    nutrition,
    patients,
    prescription,
    prompts,
    rag,
    reminders,
    security,
    symptoms,
    telemedicine,
    vectordb,
    voice,
    workflows,
)

api_router = APIRouter()
api_router.include_router(apis.router, tags=["API Catalog"])
api_router.include_router(advanced.router, tags=["Advanced AI"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(chat.router, tags=["Medical Chatbot"])
api_router.include_router(voice.router, tags=["Voice"])
api_router.include_router(hitl.router, tags=["Human-in-the-loop"])
api_router.include_router(fhir.router, tags=["FHIR/HL7"])
api_router.include_router(symptoms.router, tags=["Symptom Checker"])
api_router.include_router(appointments.router, tags=["Appointment System"])
api_router.include_router(prescription.router, tags=["Prescription Analyzer"])
api_router.include_router(lab.router, tags=["Lab Report Analyzer"])
api_router.include_router(insurance.router, tags=["Insurance Assistant"])
api_router.include_router(nutrition.router, tags=["Nutrition"])
api_router.include_router(emergency.router, tags=["Emergency Assistant"])
api_router.include_router(followup.router, tags=["Follow-up Agent"])
api_router.include_router(knowledge.router, tags=["Medical Knowledge Assistant"])
api_router.include_router(rag.router, tags=["RAG Pipeline"])
api_router.include_router(vectordb.router, tags=["Vector Database"])
api_router.include_router(embeddings.router, tags=["Embeddings"])
api_router.include_router(workflows.router, tags=["n8n Workflows"])
api_router.include_router(prompts.router, tags=["Prompt Engineering"])
api_router.include_router(database.router, tags=["Database"])
api_router.include_router(security.router, tags=["Security"])
api_router.include_router(graphrag.router, tags=["GraphRAG"])
api_router.include_router(imaging.router, tags=["Medical Image Assistant"])
api_router.include_router(reminders.router, tags=["Medication Reminder"])
api_router.include_router(telemedicine.router, tags=["Telemedicine"])
api_router.include_router(notifications.router, tags=["Notification Center"])
api_router.include_router(dashboard.router, tags=["Health Dashboard"])
api_router.include_router(patients.router, tags=["Patient Portal"])
api_router.include_router(doctors.router, tags=["Doctor Portal"])
