# How-to Update the Helm Chart Values Reference

Contributors use this README to update the generated Helm Chart values
reference in the *OX Connector for Nubus* manual.

**Important**: The Helm Chart values reference must match the published
user-facing OX Connector Helm Chart version that the documentation describes.
Operators use the reference to configure the OX Connector on Nubus for Kubernetes.

The documentation doesn't maintain the Helm Chart values reference manually.
Frigate generates the file
`docs/ox-connector/configuration/reference-values-kubernetes.txt`
from the published OX Connector Helm Chart.
The update script can also generate the reference from the local chart
for previewing unreleased changes.

The procedure below applies when the OX Connector Helm Chart version changes
or when contributors need to refresh the generated reference.

## Procedure

1. Create an issue and a merge request.
   Use the issue or merge request template that applies to your documentation change.

1. Determine the OX Connector Helm Chart version to document.

   Use the version of the published user-facing Helm Chart at:

   ```text
   oci://artifacts.software-univention.de/nubus/charts/ox-connector
   ```

   Don't use the development chart repository for published documentation
   unless the issue explicitly asks for development chart content.

1. Run the update script from the repository root in the Sphinx base container image.

   Pass the chart version as an argument:

   ```console
   $ python3 docs/ox-connector/update-helm-values-reference.py 0.42.1
   ```

   Alternatively, set the version through the environment:

   ```console
   $ OX_CONNECTOR_HELM_VERSION=0.42.1 \
      python3 docs/ox-connector/update-helm-values-reference.py
   ```

   The script downloads the published Helm Chart, generates the Frigate values
   reference, and updates:

   ```text
   docs/ox-connector/configuration/reference-values-kubernetes.txt
   ```

1. Use local mode only to preview unreleased chart changes.

   Local mode uses the chart in this repository:

   ```console
   $ python3 docs/ox-connector/update-helm-values-reference.py --local
   ```

   Don't use local mode for published documentation
   unless the issue explicitly targets unreleased chart content.
   The local chart version can differ from the published Helm Chart version.

1. Review the generated diff.

   The generated reference uses `.. envvar::` directives so that the
   documentation can link to Helm Chart values with `:envvar:`.

   To inspect added, removed, or renamed Helm Chart values, filter the diff
   for `envvar` entries:

   ```console
   $ git diff -- docs/ox-connector/configuration/reference-values-kubernetes.txt | grep "envvar"
   ```

1. Don't edit `reference-values-kubernetes.txt` manually.

   If the generated output contains missing descriptions, awkward wording,
   or spelling issues, fix the Helm Chart comments in the chart source instead
   and generate the reference again.

1. Add a document changelog entry if the update changes published content.

   Update:

   ```text
   docs/ox-connector/doc-changelog.rst
   ```

1. Wait for the repository pipeline to build the documentation.

   The pipeline runs the Sphinx build for the documentation.
   Check the pipeline result before you request a review.

1. Verify the generated reference in the built HTML output from the pipeline.

   Check the following items:

   * The Kubernetes configuration page contains the Helm Chart values reference.
   * Links to generated Helm Chart values resolve.
   * The installation guide link to the Helm Chart reference works.

1. Review your work.

   In the merge request, mention the OX Connector Helm Chart version that you used
   to generate the reference.

## Generated files

The following files define and use the generated Helm Chart values reference:

* `docs/ox-connector/.frigate` - Frigate template for the generated reference.
* `docs/ox-connector/update-helm-values-reference.py` - Update script.
* `docs/ox-connector/configuration/reference-values-kubernetes.txt` - Generated reference.
* `docs/ox-connector/configuration/kubernetes.rst` - Sphinx wrapper page that includes the generated reference.

## Verify Helm Chart value links

The generated reference creates link targets for Helm Chart values through
`.. envvar::` directives.
Content in the documentation can refer to these values with the `:envvar:` syntax.

If Sphinx can't resolve a `:envvar:` reference, the built output still shows the
link label, but not a hyperlink.
Check unresolved references in the Sphinx build output and in the rendered HTML.

## Improve generated descriptions

Frigate reads descriptions from Helm Chart comments.
If the generated reference shows `FIXME` entries or awkward wording,
the corresponding Helm Chart value likely lacks a suitable comment.

Fix such issues in the chart source and regenerate the reference.
Don't patch the generated reference directly.
