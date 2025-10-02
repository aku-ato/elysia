from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel


class QueryData(BaseModel):
    user_id: str
    conversation_id: str
    query_id: str
    query: str
    collection_names: list[str]
    route: Optional[str] = ""
    mimick: Optional[bool] = False


class ViewPaginatedCollectionData(BaseModel):
    page_size: int
    page_number: int
    query: str = ""
    sort_on: Optional[str] = None
    ascending: bool = False
    filter_config: dict[str, Any] = {}


class InitialiseTreeData(BaseModel):
    low_memory: bool = False


class MetadataNamedVectorData(BaseModel):
    name: str
    enabled: Optional[bool] = None
    description: Optional[str] = None


class MetadataFieldData(BaseModel):
    name: str
    description: str


class UpdateCollectionMetadataData(BaseModel):
    named_vectors: Optional[List[MetadataNamedVectorData]] = None
    summary: Optional[str] = None
    mappings: Optional[dict[str, dict[str, str]]] = None
    fields: Optional[List[MetadataFieldData]] = None


class NERData(BaseModel):
    text: str


class TitleData(BaseModel):
    user_id: str
    conversation_id: str
    text: str


class ObjectRelevanceData(BaseModel):
    user_id: str
    conversation_id: str
    query_id: str
    objects: list[dict]


class ProcessCollectionData(BaseModel):
    user_id: str
    collection_name: str


class DebugData(BaseModel):
    conversation_id: str
    user_id: str


class AddFeedbackData(BaseModel):
    user_id: str
    conversation_id: str
    query_id: str
    feedback: int


class RemoveFeedbackData(BaseModel):
    user_id: str
    conversation_id: str
    query_id: str


class GetUserRequestsData(BaseModel):
    user_id: str


class InstantReplyData(BaseModel):
    user_id: str
    user_prompt: str


class FollowUpSuggestionsData(BaseModel):
    user_id: str
    conversation_id: str


# class BackendConfig(BaseModel):
#     settings: dict[str, Any]
#     style: str
#     agent_description: str
#     end_goal: str
#     branch_initialisation: str


class SaveConfigUserData(BaseModel):
    name: str
    config: dict[str, Any]
    frontend_config: dict[str, Any]
    default: bool


class SaveConfigTreeData(BaseModel):
    settings: Optional[dict[str, Any]] = None
    style: Optional[str] = None
    agent_description: Optional[str] = None
    end_goal: Optional[str] = None
    branch_initialisation: Optional[str] = None


class UpdateFrontendConfigData(BaseModel):
    config: dict[str, Any]


class AddToolToTreeData(BaseModel):
    tool_name: str
    branch_id: str
    from_tool_ids: list[str]


class RemoveToolFromTreeData(BaseModel):
    tool_name: str
    branch_id: str
    from_tool_ids: list[str]


class AddBranchToTreeData(BaseModel):
    id: str
    description: str
    instruction: str
    from_branch_id: str
    from_tool_ids: list[str]
    status: str
    root: bool


class RemoveBranchFromTreeData(BaseModel):
    id: str


class AvailableModelsData(BaseModel):
    user_id: str


# Collection Management Data Models
class PropertyDefinition(BaseModel):
    name: str
    data_type: str  # "text", "int", "number", "bool", "date", "object", "text[]", etc.
    tokenization: Optional[str] = None  # "word", "lowercase", "whitespace", "field"
    nested_properties: Optional[List["PropertyDefinition"]] = None


class VectorizerConfig(BaseModel):
    type: str  # "none", "text2vec-openai", "text2vec-cohere", etc.
    model: Optional[str] = None
    vectorize_collection_name: Optional[bool] = False


class NamedVectorConfig(BaseModel):
    name: str
    vectorizer_type: str
    model: Optional[str] = None
    source_properties: Optional[List[str]] = None


class CreateCollectionData(BaseModel):
    collection_name: str
    properties: List[PropertyDefinition]
    vectorizer_config: Optional[VectorizerConfig] = None
    named_vectors: Optional[List[NamedVectorConfig]] = None
    description: Optional[str] = None


class InsertObjectsData(BaseModel):
    objects: List[Dict[str, Any]]  # List of objects to insert


class DeleteCollectionData(BaseModel):
    collection_name: str
    confirm: bool = False  # Safety flag to prevent accidental deletion
