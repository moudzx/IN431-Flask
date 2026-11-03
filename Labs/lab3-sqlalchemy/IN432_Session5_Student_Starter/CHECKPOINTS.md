# Named checks in the same project

Run each from the project root. Prefix every group below with
python -m unittest and finish with -v.

Setup: checks.SetupChecks
A1: checks.ModelChecks
A2: checks.RepresentationChecks
A3: checks.CreateChecks
A4: checks.ListChecks
A5: checks.UpdateChecks
A6: checks.DeleteChecks
Transaction demonstration: checks.TransactionChecks
B1: checks.ProjectModelChecks
B2: checks.ProjectChecks
C1: checks.DetailsModelChecks
C2: checks.DetailsChecks
D1: checks.TagModelChecks
D2 and D3: checks.TagChecks
E1 and E2: checks.ReportChecks
E3: checks.BundleChecks
After all mappings and upgrades: checks.SchemaChecks

Run the whole suite only after all exercises. Initial SetupChecks passes without
the model TODOs. A later group depends on its earlier mappings and methods.
Tests build temporary databases matching the current model; the manual schema
upgrade and returned-id evidence checks your working database file.
