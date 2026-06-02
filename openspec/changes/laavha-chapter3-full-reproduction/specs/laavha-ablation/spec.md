## ADDED Requirements

### Requirement: LAAVHA-L Variant (No LSTM Prediction)

The inference server SHALL support a LAAVHA-L ablation variant that removes
the LSTM prediction module while retaining the Attention weight mechanism.

#### Scenario: Skip LSTM prediction

- **WHEN** algorithm="laavha-l" is selected
- **THEN** the algorithm SHALL use current-step network state directly as the
  decision matrix instead of LSTM-predicted future state
- **THEN** the Attention module SHALL still compute dynamic weights from current state

#### Scenario: Model loading unchanged

- **WHEN** LAAVHA-L runs
- **THEN** the algorithm SHALL still load the full LAAVHA_Net model weights
- **THEN** only the LSTM prediction output SHALL be replaced; Attention output
  SHALL be used normally

### Requirement: LAAVHA-A Variant (No Attention Weights)

The inference server SHALL support a LAAVHA-A ablation variant that removes
the Attention dynamic weight module while retaining LSTM prediction.

#### Scenario: Replace Attention with entropy weights

- **WHEN** algorithm="laavha-a" is selected
- **THEN** the algorithm SHALL use LSTM-predicted future state as the decision matrix
- **THEN** the algorithm SHALL replace Attention-generated weights with entropy-method
  uniform weights

#### Scenario: Model loading unchanged

- **WHEN** LAAVHA-A runs
- **THEN** the algorithm SHALL still load the full LAAVHA_Net model weights
- **THEN** only the Attention weight output SHALL be discarded; LSTM prediction
  SHALL be used normally

### Requirement: Ablation Fair Comparison

Both ablation variants SHALL use the same trained model checkpoint, evaluation
mode (model.eval()), and decision pipeline as the full LAAVHA algorithm to ensure
controlled variable comparison.

#### Scenario: Same model weights

- **WHEN** LAAVHA, LAAVHA-L, and LAAVHA-A are compared
- **THEN** all three SHALL load from the same model file
- **THEN** all three SHALL use strict=True loading

#### Scenario: Same normalization and scoring

- **WHEN** computing final network scores
- **THEN** all three variants SHALL use identical min-max normalization
- **THEN** all three SHALL use identical benefit/cost index definitions
