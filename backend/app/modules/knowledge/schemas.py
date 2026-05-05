from typing import Literal

from pydantic import Field

from backend.app.schemas.common import SchemaModel


class KnowledgeMetric(SchemaModel):
    label: str
    value: str
    note: str


class KnowledgeOverviewCard(SchemaModel):
    highlight: str
    title: str
    summary: str
    hint: str


class KnowledgeStandard(SchemaModel):
    title: str
    category: str
    summary: str
    update: str
    applicable_to: str = Field(serialization_alias="applicableTo")
    checkpoints: list[str]


class KnowledgeStrategy(SchemaModel):
    title: str
    trigger: str
    response: str
    deliverable: str
    collaboration: str


class KnowledgeCase(SchemaModel):
    title: str
    site: str
    issue: str
    symptom: str
    diagnosis: str
    method: str
    outcome: str
    caution: str
    tags: list[str]


class KnowledgeChecklist(SchemaModel):
    title: str
    items: list[str]


class KnowledgeQuestion(SchemaModel):
    question: str
    answer: str
    recommendation: str
    references: list[str]


class KnowledgeReference(SchemaModel):
    title: str
    url: str
    excerpt: str


class KnowledgeRecommendation(SchemaModel):
    result_id: str = Field(serialization_alias="resultId")
    title: str
    severity: str
    trigger_reason: str = Field(serialization_alias="triggerReason")
    suggested_standard: str = Field(serialization_alias="suggestedStandard")
    recommended_action: str = Field(serialization_alias="recommendedAction")
    checklist_title: str = Field(serialization_alias="checklistTitle")
    work_order_status: str = Field(serialization_alias="workOrderStatus")
    references: list[KnowledgeReference]


class KnowledgeRouteAction(SchemaModel):
    kind: Literal["route"]
    title: str
    entry_label: str = Field(serialization_alias="entryLabel")
    target: str


class KnowledgeExternalAction(SchemaModel):
    kind: Literal["external"]
    title: str
    entry_label: str = Field(serialization_alias="entryLabel")
    target: str


KnowledgeAction = KnowledgeRouteAction | KnowledgeExternalAction


class KnowledgePagePayload(SchemaModel):
    knowledge_metrics: list[KnowledgeMetric] = Field(serialization_alias="knowledgeMetrics")
    knowledge_overview: list[KnowledgeOverviewCard] = Field(serialization_alias="knowledgeOverview")
    knowledge_standards: list[KnowledgeStandard] = Field(serialization_alias="knowledgeStandards")
    knowledge_strategies: list[KnowledgeStrategy] = Field(serialization_alias="knowledgeStrategies")
    knowledge_cases: list[KnowledgeCase] = Field(serialization_alias="knowledgeCases")
    knowledge_checklists: list[KnowledgeChecklist] = Field(serialization_alias="knowledgeChecklists")
    knowledge_questions: list[KnowledgeQuestion] = Field(serialization_alias="knowledgeQuestions")
    knowledge_actions: list[KnowledgeAction] = Field(serialization_alias="knowledgeActions")
    knowledge_recommendations: list[KnowledgeRecommendation] = Field(
        default_factory=list,
        serialization_alias="knowledgeRecommendations",
    )
