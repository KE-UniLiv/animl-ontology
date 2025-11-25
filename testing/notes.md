
Not addressed | To inspect 

- CQ-3: Is a specific sample derived from another sample?
    - J: Not in the Graffoo. Do we have this reflexive property?
- CQ-6: What is the unique identifier of the device?
    - Do we have a serialNumber or is this the identifier or shall we use the more general aml:id defined on owl:Thing(s)?
- CQ-13: What is the conversion factor for a unit to its SI base representation?
    - I don't think we support this one.
- CQ-14: What is the increment value for an auto-incremented series?
    - Do we have an aml:increment data property?
- Please check CQ-22, CQ-23, CQ-28, CQ-41

- CQ-29: What is the role of an author within their organization?
    - Do we have an aml:author object property connecting document with Agent or does this rely on the role?

- CQ-32: Who is the manufacturer of the device?
    - I guess we do not have a manifacturer property.
    - The same applies to CQ-82

- CQ-42: Is a sample with a specific role required or optional for a technique?
    - This query is wrong, and we should check whether the ontology supports this.

- CQ-47: When was an experiment step performed?
    - Please check. Time can also refer to the relative order within the sequence of steps (if this is all we have).

- CQ-51: Was a sample in an experiment step inherited from a parent step?
    - Ovdercomplicated, which may suggest that modelling could be improved there.

- IMPORTANT: CQ-52 | To check, as the bindings are not convincing

- CQ-53: Is a specific result required by a technique's definition?
    - No modality used. This should be simpler

- Do we keep track of the author of a method? (CQ-54)
    - Similar consideration for CQ-61
    - Similar for CQ-67

- Do we keep track of the firmware version of software/devices? (CQ-63)

- Do we have an aml:email property?

- Not sure about CQ-75

- Please check CQ-78

- CQ-83: Is a given technique definition abstract, requiring an extension?
    - I am not sure whether we fully support this

- CQ-85: to check and reformulate

- CQ:90: to check

- CQ:99: check if we model aml:affiliation

- Not sure about the clarity of CQ-102