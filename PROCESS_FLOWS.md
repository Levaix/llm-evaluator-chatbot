# Process Flow Diagrams

> **📊 Viewing Diagrams**: This document contains Mermaid flowcharts. To view them:
> - **Easiest**: View on GitHub/GitLab (auto-renders)
> - **VS Code**: Install "Markdown Preview Mermaid Support" extension
> - **Online**: Copy diagram code to https://mermaid.live/
> - **See**: `README.md` section "Viewing Diagrams" for detailed instructions

This document provides detailed process flow diagrams for all major workflows in the LLM Evaluator Chatbot system.

## Table of Contents
1. [User Interaction Flow](#user-interaction-flow)
2. [Evaluation Process Flow](#evaluation-process-flow)
3. [Data Processing Pipeline](#data-processing-pipeline)
4. [Feedback Collection Flow](#feedback-collection-flow)
5. [System Initialization Flow](#system-initialization-flow)
6. [Error Handling Flow](#error-handling-flow)

---

## User Interaction Flow

### Complete User Journey

```mermaid
flowchart TD
    Start([User Opens Application]) --> LoadUI[Load Streamlit UI]
    LoadUI --> InitSession[Initialize Session State]
    InitSession --> LoadDataset{Dataset<br/>Loaded?}
    
    LoadDataset -->|No| LoadData[Load Q&A Dataset]
    LoadData --> ValidateData{Valid<br/>Dataset?}
    ValidateData -->|No| ShowError[Show Error Message]
    ValidateData -->|Yes| SelectQuestion[Select Random Question]
    
    LoadDataset -->|Yes| SelectQuestion
    SelectQuestion --> DisplayQuestion[Display Question to User]
    
    DisplayQuestion --> UserAction{User Action}
    
    UserAction -->|New Question| SelectQuestion
    UserAction -->|Enter Answer| InputAnswer[User Types Answer]
    UserAction -->|Generate Novice| GenerateNovice[Generate Novice Answer]
    GenerateNovice --> InputAnswer
    
    InputAnswer --> SubmitAnswer{Submit<br/>Answer?}
    SubmitAnswer -->|No| UserAction
    SubmitAnswer -->|Yes| StartEvaluation[Start Evaluation Process]
    
    StartEvaluation --> ShowSpinner[Show Loading Spinner]
    ShowSpinner --> EvalProcess[Evaluation Process]
    EvalProcess --> DisplayResults[Display Results]
    
    DisplayResults --> FeedbackOption{Provide<br/>Feedback?}
    FeedbackOption -->|Yes| CollectFeedback[Collect User Feedback]
    FeedbackOption -->|No| UserAction
    
    CollectFeedback --> AnalyzeSentiment[Analyze Sentiment]
    AnalyzeSentiment --> LogFeedback[Log Evaluation + Feedback]
    LogFeedback --> UserAction
    
    ShowError --> End([End])
    UserAction -->|Exit| End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style EvalProcess fill:#fff4e1
    style DisplayResults fill:#e8f5e9
    style ShowError fill:#ffebee
```

### Question Selection Flow

```mermaid
flowchart LR
    Start([User Clicks<br/>New Question]) --> CheckDataset{Dataset in<br/>Session?}
    CheckDataset -->|No| LoadDataset[Load Dataset from File]
    CheckDataset -->|Yes| SelectRandom[Select Random Question]
    
    LoadDataset --> ValidateJSON{Valid<br/>JSON?}
    ValidateJSON -->|No| Error[Show Error]
    ValidateJSON -->|Yes| ParseData[Parse JSON to DataFrame]
    ParseData --> ValidateStructure{Valid<br/>Structure?}
    ValidateStructure -->|No| Error
    ValidateStructure -->|Yes| StoreDataset[Store in Session State]
    
    StoreDataset --> SelectRandom
    SelectRandom --> UpdateUI[Update UI with Question]
    UpdateUI --> ClearAnswer[Clear Previous Answer]
    ClearAnswer --> End([Ready for Answer])
    
    Error --> End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5e9
    style Error fill:#ffebee
```

---

## Evaluation Process Flow

### Complete Evaluation Pipeline

```mermaid
flowchart TD
    Start([Evaluation Request]) --> ValidateInput{Input<br/>Valid?}
    ValidateInput -->|No| ReturnError[Return Error]
    ValidateInput -->|Yes| BuildPrompt[Build Evaluation Prompt]
    
    BuildPrompt --> CreateMessages[Create Message Array]
    CreateMessages --> AddSystemPrompt[Add System Prompt]
    AddSystemPrompt --> AddUserPrompt[Add User Prompt with Question/Answers]
    
    AddUserPrompt --> CheckClient{OpenAI Client<br/>Exists?}
    CheckClient -->|No| InitClient[Initialize OpenAI Client]
    CheckClient -->|Yes| CallAPI[Call OpenAI API]
    InitClient --> CallAPI
    
    CallAPI --> APIResponse{API<br/>Success?}
    APIResponse -->|No| HandleError[Handle API Error]
    APIResponse -->|Yes| ExtractResponse[Extract LLM Response]
    
    ExtractResponse --> ParseScore[Parse Score from Text]
    ParseScore --> ValidateScore{Score<br/>Valid?}
    ValidateScore -->|No| DefaultScore[Use Default Score: 50]
    ValidateScore -->|Yes| ComputeROUGE[Compute ROUGE Metrics]
    DefaultScore --> ComputeROUGE
    
    ComputeROUGE --> LoadROUGEMetric{ROUGE Metric<br/>Loaded?}
    LoadROUGEMetric -->|No| LoadMetric[Load ROUGE Metric]
    LoadROUGEMetric -->|Yes| CalculateROUGE[Calculate ROUGE-1 & ROUGE-L]
    LoadMetric --> CalculateROUGE
    
    CalculateROUGE --> CreateResult[Create EvaluationResult]
    CreateResult --> ReturnResult[Return Result]
    
    HandleError --> ReturnError
    ReturnError --> End([End with Error])
    ReturnResult --> End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style CallAPI fill:#fff4e1
    style ReturnResult fill:#e8f5e9
    style ReturnError fill:#ffebee
```

### Prompt Building Process

```mermaid
flowchart TD
    Start([Build Prompt Request]) --> ReceiveInput[Receive: Question, Reference, Student Answer, Language]
    ReceiveInput --> CreateTemplate[Create Prompt Template]
    
    CreateTemplate --> AddTask[Add Task Description]
    AddTask --> AddQuestion[Insert Question Text]
    AddQuestion --> AddReference[Insert Reference Answer]
    AddReference --> AddStudent[Insert Student Answer]
    
    AddStudent --> AddSteps[Add 6-Step Evaluation Process]
    AddSteps --> AddStep1[Step 1: Content Analysis]
    AddStep1 --> AddStep2[Step 2: Correctness Assessment]
    AddStep2 --> AddStep3[Step 3: Semantic Equivalence]
    AddStep3 --> AddStep4[Step 4: Completeness]
    AddStep4 --> AddStep5[Step 5: Scoring Rubric]
    AddStep5 --> AddStep6[Step 6: Constructive Explanation]
    
    AddStep6 --> AddRubric[Add Detailed Scoring Rubric]
    AddRubric --> AddFormat[Add Response Format Instructions]
    AddFormat --> InsertLanguage[Insert Language Parameter]
    InsertLanguage --> FormatPrompt[Format Complete Prompt]
    FormatPrompt --> ReturnPrompt[Return Formatted Prompt]
    ReturnPrompt --> End([Prompt Ready])
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
```

### Score Parsing Process

```mermaid
flowchart TD
    Start([Parse Score from Text]) --> ReceiveText[Receive LLM Response Text]
    ReceiveText --> TryPattern1[Try Pattern: 'Score: \d+']
    TryPattern1 --> Match1{Match<br/>Found?}
    
    Match1 -->|Yes| ExtractScore1[Extract Score]
    Match1 -->|No| TryPattern2[Try Pattern: 'score = \d+']
    
    TryPattern2 --> Match2{Match<br/>Found?}
    Match2 -->|Yes| ExtractScore2[Extract Score]
    Match2 -->|No| TryPattern3[Try Pattern: 'score of \d+']
    
    TryPattern3 --> Match3{Match<br/>Found?}
    Match3 -->|Yes| ExtractScore3[Extract Score]
    Match3 -->|No| TryContext[Search Near 'score' Keyword]
    
    TryContext --> MatchContext{Match<br/>Found?}
    MatchContext -->|Yes| ExtractContext[Extract Number]
    MatchContext -->|No| TryLastLines[Search Last 5 Lines]
    
    TryLastLines --> MatchLines{Valid<br/>Number?}
    MatchLines -->|Yes| ExtractLines[Extract Score]
    MatchLines -->|No| UseDefault[Use Default: 50]
    
    ExtractScore1 --> ValidateRange{Score in<br/>0-100?}
    ExtractScore2 --> ValidateRange
    ExtractScore3 --> ValidateRange
    ExtractContext --> ValidateRange
    ExtractLines --> ValidateRange
    
    ValidateRange -->|Yes| ClampScore[Clamp to 0-100]
    ValidateRange -->|No| ClampScore
    UseDefault --> ClampScore
    
    ClampScore --> ReturnScore[Return Score]
    ReturnScore --> End([Score Parsed])
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style UseDefault fill:#fff4e1
```

---

## Data Processing Pipeline

### Dataset Loading Flow

```mermaid
flowchart TD
    Start([Load Dataset Request]) --> CheckPath{File<br/>Exists?}
    CheckPath -->|No| FileError[Raise FileNotFoundError]
    CheckPath -->|Yes| ReadFile[Read JSON File]
    
    ReadFile --> ParseJSON{Valid<br/>JSON?}
    ParseJSON -->|No| JSONError[Raise JSONDecodeError]
    ParseJSON -->|Yes| CheckType{Is<br/>List?}
    
    CheckType -->|No| TypeError[Raise ValueError]
    CheckType -->|Yes| CheckEmpty{Empty<br/>List?}
    
    CheckEmpty -->|Yes| EmptyError[Raise ValueError]
    CheckEmpty -->|No| ValidateItems[Validate Each Item]
    
    ValidateItems --> CheckFields{Has 'question'<br/>and 'answer'?}
    CheckFields -->|No| FieldError[Raise ValueError]
    CheckFields -->|Yes| CheckEmptyFields{Fields<br/>Non-Empty?}
    
    CheckEmptyFields -->|No| SkipItem[Skip Item with Warning]
    CheckEmptyFields -->|Yes| AddRecord[Add to Records List]
    
    SkipItem --> NextItem{More<br/>Items?}
    AddRecord --> NextItem
    
    NextItem -->|Yes| ValidateItems
    NextItem -->|No| CheckRecords{Any Valid<br/>Records?}
    
    CheckRecords -->|No| NoRecordsError[Raise ValueError]
    CheckRecords -->|Yes| CreateDataFrame[Create pandas DataFrame]
    CreateDataFrame --> AddIDs[Add ID Column]
    AddIDs --> ReturnDF[Return DataFrame]
    ReturnDF --> End([Dataset Loaded])
    
    FileError --> End
    JSONError --> End
    TypeError --> End
    EmptyError --> End
    FieldError --> End
    NoRecordsError --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style FileError fill:#ffebee
    style JSONError fill:#ffebee
    style TypeError fill:#ffebee
```

### Logging Flow

```mermaid
flowchart TD
    Start([Log Evaluation Request]) --> CreateRecord[Create Log Record]
    CreateRecord --> AddTimestamp[Add Timestamp]
    AddTimestamp --> AddQuestionData[Add Question ID & Text]
    AddQuestionData --> AddAnswers[Add Reference & Student Answers]
    AddAnswers --> AddScores[Add LLM Score & ROUGE Metrics]
    AddScores --> AddExplanation[Add LLM Explanation]
    AddExplanation --> AddFeedback{Feedback<br/>Provided?}
    
    AddFeedback -->|Yes| AddFeedbackTags[Add Feedback Tags]
    AddFeedbackTags --> AddFeedbackText[Add Feedback Text]
    AddFeedbackText --> AddSentiment[Add Sentiment Analysis]
    AddFeedback -->|No| SerializeJSON[Serialize to JSON]
    AddSentiment --> SerializeJSON
    
    SerializeJSON --> CheckFile{Log File<br/>Exists?}
    CheckFile -->|No| CreateFile[Create Log File]
    CheckFile -->|Yes| AppendFile[Append to Log File]
    CreateFile --> AppendFile
    
    AppendFile --> Success{Write<br/>Success?}
    Success -->|Yes| LogSuccess[Log Success Message]
    Success -->|No| LogError[Log Error & Show Warning]
    
    LogSuccess --> End([Logged])
    LogError --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style LogError fill:#ffebee
```

---

## Feedback Collection Flow

### Complete Feedback Process

```mermaid
flowchart TD
    Start([User Provides Feedback]) --> CheckEvaluation{Evaluation<br/>Exists?}
    CheckEvaluation -->|No| ShowMessage[Show: No Evaluation Yet]
    CheckEvaluation -->|Yes| DisplayFeedbackUI[Display Feedback UI]
    
    DisplayFeedbackUI --> SelectTags[User Selects Tags]
    SelectTags --> EnterText{Enter<br/>Text?}
    
    EnterText -->|Yes| InputText[User Enters Feedback Text]
    EnterText -->|No| CheckSubmit{Submit<br/>Feedback?}
    
    InputText --> CheckSubmit
    CheckSubmit -->|No| DisplayFeedbackUI
    CheckSubmit -->|Yes| ValidateFeedback{Has Tags<br/>or Text?}
    
    ValidateFeedback -->|No| ShowWarning[Show Warning: Provide Feedback]
    ValidateFeedback -->|Yes| CheckText{Has<br/>Text?}
    
    ShowWarning --> DisplayFeedbackUI
    CheckText -->|Yes| AnalyzeSentiment[Analyze Sentiment]
    CheckText -->|No| PrepareLog[Prepare Log Record]
    
    AnalyzeSentiment --> LoadModel{Sentiment Model<br/>Loaded?}
    LoadModel -->|No| LoadSentimentModel[Load DistilBERT Model]
    LoadModel -->|Yes| ProcessText[Process Feedback Text]
    LoadSentimentModel --> ProcessText
    
    ProcessText --> GetSentiment[Get Sentiment Label & Score]
    GetSentiment --> PrepareLog
    PrepareLog --> LogEvaluation[Log Evaluation with Feedback]
    
    LogEvaluation --> ShowSuccess[Show Success Message]
    ShowSuccess --> DisplaySentiment{Sentiment<br/>Available?}
    DisplaySentiment -->|Yes| ShowSentiment[Display Sentiment Result]
    DisplaySentiment -->|No| ClearFeedback[Clear Feedback Inputs]
    ShowSentiment --> ClearFeedback
    
    ClearFeedback --> RefreshUI[Refresh UI]
    RefreshUI --> End([Feedback Submitted])
    ShowMessage --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style ShowWarning fill:#fff4e1
    style ShowSuccess fill:#e8f5e9
```

---

## System Initialization Flow

### Application Startup

```mermaid
flowchart TD
    Start([Application Start]) --> ImportModules[Import All Modules]
    ImportModules --> LoadConfig[Load Configuration Module]
    
    LoadConfig --> CheckEnvVars[Check Environment Variables]
    CheckEnvVars --> CheckAPIKey{API Key<br/>Set?}
    
    CheckAPIKey -->|No| WarnAPIKey[Log Warning: API Key Missing]
    CheckAPIKey -->|Yes| EnsureDirs[Ensure Directories Exist]
    WarnAPIKey --> EnsureDirs
    
    EnsureDirs --> CheckDataDir{Data Directory<br/>Exists?}
    CheckDataDir -->|No| CreateDataDir[Create Data Directory]
    CheckDataDir -->|Yes| CheckLogDir{Log Directory<br/>Exists?}
    CreateDataDir --> CheckLogDir
    
    CheckLogDir -->|No| CreateLogDir[Create Log Directory]
    CheckLogDir -->|Yes| InitStreamlit[Initialize Streamlit]
    CreateLogDir --> InitStreamlit
    
    InitStreamlit --> SetPageConfig[Set Page Configuration]
    SetPageConfig --> InitSessionState[Initialize Session State]
    
    InitSessionState --> InitQuestion[Initialize: current_question = None]
    InitQuestion --> InitEvaluation[Initialize: last_evaluation = None]
    InitEvaluation --> InitDataset[Initialize: dataset = None]
    InitDataset --> InitShowRef[Initialize: show_reference = False]
    InitShowRef --> InitLanguage[Initialize: language = 'English']
    
    InitLanguage --> RenderUI[Render UI Components]
    RenderUI --> End([Application Ready])
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style WarnAPIKey fill:#fff4e1
```

### Module Initialization

```mermaid
flowchart TD
    Start([Module Import]) --> ImportDependencies[Import Dependencies]
    ImportDependencies --> SetLogging[Set Up Logging]
    SetLogging --> ModuleSpecific{Module<br/>Type?}
    
    ModuleSpecific -->|Config| LoadEnvVars[Load Environment Variables]
    ModuleSpecific -->|LLM Interface| InitClientVar[Initialize Client Variable = None]
    ModuleSpecific -->|Evaluator| InitROUGEVar[Initialize ROUGE Variable = None]
    ModuleSpecific -->|Sentiment| InitSentimentVar[Initialize Sentiment Variable = None]
    
    LoadEnvVars --> SetDefaults[Set Default Values]
    SetDefaults --> EnsureDirs[Ensure Directories]
    EnsureDirs --> End([Module Ready])
    
    InitClientVar --> End
    InitROUGEVar --> End
    InitSentimentVar --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
```

---

## Error Handling Flow

### API Error Handling

```mermaid
flowchart TD
    Start([API Call]) --> TryCall[Try API Call]
    TryCall --> CheckSuccess{Call<br/>Success?}
    
    CheckSuccess -->|Yes| ExtractContent[Extract Response Content]
    ExtractContent --> ValidateContent{Content<br/>Valid?}
    ValidateContent -->|Yes| ReturnContent[Return Content]
    ValidateContent -->|No| HandleEmpty[Handle Empty Response]
    HandleEmpty --> ReturnDefault[Return Empty String]
    
    CheckSuccess -->|No| CatchError[Catch OpenAIError]
    CatchError --> LogError[Log Error Details]
    LogError --> CheckErrorType{Error<br/>Type?}
    
    CheckErrorType -->|401 Unauthorized| AuthError[Raise: Missing/Invalid API Key]
    CheckErrorType -->|429 Rate Limit| RateLimitError[Raise: Rate Limit Exceeded]
    CheckErrorType -->|500+ Server Error| ServerError[Raise: Service Unavailable]
    CheckErrorType -->|Other| GenericError[Raise: Generic API Error]
    
    AuthError --> ShowUserError[Show User-Friendly Error]
    RateLimitError --> ShowUserError
    ServerError --> ShowUserError
    GenericError --> ShowUserError
    
    ShowUserError --> End([Error Handled])
    ReturnContent --> End
    ReturnDefault --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style ShowUserError fill:#ffebee
```

### Data Validation Flow

```mermaid
flowchart TD
    Start([Data Input]) --> ValidateType{Correct<br/>Type?}
    ValidateType -->|No| TypeError[Raise TypeError]
    ValidateType -->|Yes| ValidateNotEmpty{Not<br/>Empty?}
    
    ValidateNotEmpty -->|No| EmptyError[Raise ValueError]
    ValidateNotEmpty -->|Yes| ValidateFormat{Correct<br/>Format?}
    
    ValidateFormat -->|No| FormatError[Raise ValueError]
    ValidateFormat -->|Yes| ValidateRange{In Valid<br/>Range?}
    
    ValidateRange -->|No| RangeError[Raise ValueError]
    ValidateRange -->|Yes| ValidateStructure{Correct<br/>Structure?}
    
    ValidateStructure -->|No| StructureError[Raise ValueError]
    ValidateStructure -->|Yes| ReturnValid[Return Valid Data]
    
    TypeError --> ShowError[Show Error to User]
    EmptyError --> ShowError
    FormatError --> ShowError
    RangeError --> ShowError
    StructureError --> ShowError
    
    ShowError --> End([Validation Complete])
    ReturnValid --> End
    
    style Start fill:#e1f5ff
    style End fill:#e8f5e9
    style ShowError fill:#ffebee
```

---

## Summary

These process flows document the complete workflows for:

1. **User Interactions**: Complete user journey from application start to feedback submission
2. **Evaluation Process**: Detailed evaluation pipeline from input to result
3. **Data Processing**: Dataset loading and logging procedures
4. **Feedback Collection**: User feedback gathering and sentiment analysis
5. **System Initialization**: Application and module startup procedures
6. **Error Handling**: Comprehensive error handling and recovery

All flows are designed to be:
- **Clear**: Easy to understand and follow
- **Complete**: Cover all major paths and edge cases
- **Maintainable**: Easy to update as system evolves
- **Documented**: Support development and debugging

These diagrams can be used for:
- Understanding system behavior
- Onboarding new developers
- Debugging issues
- Planning enhancements
- Documentation for stakeholders

