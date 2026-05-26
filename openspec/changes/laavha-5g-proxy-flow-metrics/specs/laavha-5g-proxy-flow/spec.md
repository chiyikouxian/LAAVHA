## ADDED Requirements

### Requirement: 5G Proxy Traffic Metrics

The LAAVHA ns3-ai handover example SHALL provide ns-3-generated traffic metrics
for the 5G candidate when real NR/5G-LENA is unavailable.

#### Scenario: FlowMonitor feeds 5G proxy metrics

- **WHEN** the example runs in `flowmonMode=feed`
- **THEN** candidate index `0` SHALL receive delay, throughput, and PLR values
  derived from a FlowMonitor-observed 5G proxy traffic flow

#### Scenario: Message schema remains stable

- **WHEN** 5G proxy flow metrics are added
- **THEN** the C++ to Python and Python to C++ ns3-ai message structures SHALL
  remain unchanged

### Requirement: 5G Proxy Labeling

The system SHALL label the 5G candidate as proxy/synthetic unless a real
NR/5G-LENA module is integrated.

#### Scenario: Runtime source reporting

- **WHEN** the example starts
- **THEN** logs SHALL identify 5G as a proxy candidate and SHALL NOT claim that
  it is real NR

#### Scenario: Metric source reporting

- **WHEN** 5G metrics are logged or documented
- **THEN** SINR/RSRP SHALL be labeled as propagation proxy and
  delay/throughput/PLR SHALL be labeled as FlowMonitor proxy flow metrics

### Requirement: Candidate Isolation

The 5G proxy flow SHALL be distinguishable from WiFi and LTE flows.

#### Scenario: Flow classification

- **WHEN** FlowMonitor reports multiple flows
- **THEN** the implementation SHALL classify the 5G proxy flow without
  aggregating it with WiFi or LTE metrics

#### Scenario: Existing candidate preservation

- **WHEN** the 5G proxy flow is enabled
- **THEN** WiFi and LTE metric sources SHALL continue to work as before
