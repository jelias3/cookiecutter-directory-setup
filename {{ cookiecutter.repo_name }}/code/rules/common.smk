import pandas as pd
import os
import sys
import filecmp
import pathlib


# try/except useful for running this script in isolation in interactive shell
# for debugging
#
# `.set_index("Sample", drop=False)` rather than `index_col=0`: it gives the same index but
# KEEPS the Sample column, which snakemake's validate() needs -- validate() sees each row's
# columns and not the index, so with the column dropped a `required: [Sample]` schema fails
# on every row.
try:
    samples = pd.read_csv(config["samples"], sep='\t').set_index("Sample", drop=False)
except (NameError, KeyError) as NameOrKeyError:
    samples = pd.read_csv("config/samples.tsv", sep='\t').set_index("Sample", drop=False)

# Validate the sample sheet against code/schemas/samples.schema.yaml. Shipped COMMENTED
# because the schema's columns and its Sample-ID pattern describe the template's example
# sheet, not yours yet -- uncomment once samples.tsv has its real columns and the schema
# matches them. Leaving it commented is a choice with a cost: nothing checks your sample
# IDs, and a typo'd ID silently becomes a new sample with its own output tree.
#
# from snakemake.utils import validate
# validate(samples, schema="../schemas/samples.schema.yaml")

# Add code for function definitions and other things that must be defined prior
# to rest of workflow (eg custom snakemake input functions)
def has_differences(dcmp):
    """
    https://stackoverflow.com/questions/4187564/recursively-compare-two-directories-to-ensure-they-have-the-same-files-and-subdi
    """
    try:
        differences = dcmp.left_only + dcmp.right_only + dcmp.diff_files
        if differences:
            return True
        return any([has_differences(subdcmp) for subdcmp in dcmp.subdirs.values()])
    except NotADirectoryError:
        return True

def CreateSymlinksOfDir1ContentsIntoDir2(Dir1, Dir2):
    """
    helper function to create symlinks for scripts... Imagine a snakemake rule
    defined in a module workflow with shell directive...
    shell: 'Rscript myRscriptWithRelativeFilepathRelativeToModuleWorkflow.R SomeMoreArgs'
    ...This rule will only work if
    myRscriptWithRelativeFilepathRelativeToModuleWorkflow.R exists in the
    workdir for the main Snakefile.
    """
    Dir1_sanitized = Dir1.rstrip("/") + "/"
    Dir2_sanitized = Dir2.rstrip("/") + "/"
    for filepath in pathlib.Path(Dir1_sanitized).glob('*'):
        module_script_file = os.path.abspath(filepath)
        new_script_link = Dir2_sanitized + os.path.basename(filepath)
        try:
            os.symlink(module_script_file, new_script_link)
            print(f'Making link: {new_script_link}->{module_script_file}', file=sys.stderr)
        except FileExistsError:
            if filecmp.cmp(module_script_file, new_script_link) or not has_differences(filecmp.dircmp(module_script_file, new_script_link)):
                # print(f'{new_script_link}->{module_script_file} already exists', file=sys.stderr)
                pass
            # elif os.readlink(new_script_link)==module_script_file:
            #     pass
            else:
                print(f'not making link, fix clashing file names: {new_script_link}->{module_script_file}', file=sys.stderr)

