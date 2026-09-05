# InvenTree inventory assistance

This context describes inventory records and the review process for changes proposed through an assistant.

## Language

**Allowed user**:
A person whose personal credential is accepted by the configured InvenTree instance. Their inventory actions remain limited by their InvenTree permissions; there is no separate manually maintained admission list.

**Linked credential**:
A user's InvenTree API token entrusted to the integration for requests to that user's inventory instance. It is distinct from the credential used to connect an AI client to the integration.

**Part**:
A catalog definition of an item that may be held in inventory.
_Avoid_: Using “stock item” for the catalog definition.

**Stock item**:
A tracked quantity of a part held in inventory, with its own location and stock-specific information.
_Avoid_: Using “part” for a particular quantity in storage.

**Stock location**:
A named place in which inventory is stored; locations may form a hierarchy.

**Change Plan**:
A reviewable description of proposed inventory changes before they are carried out.
_Avoid_: Calling a proposal an approved or completed change.

**Intake**:
The process of interpreting incoming items, identifying their catalog records, and preparing their receipt into inventory.

**Enrichment**:
Adding supported descriptive information, specifications, images, or reference documents to a catalog part.
