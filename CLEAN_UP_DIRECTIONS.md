# Cleanup Directions: 04-01-2026, 11 PM 

## Project: Library and Outputs for Thorough Study of the Reduced Register and the Canonical Register

### JSON Schema

- There is a complete JSON schema version 5.0 which is a computational representation of the differences between the two registers. The differences are based on information about the surface forms (sentences) of both registers, using a parallel corpus of the two from three English newspapers (in the input directory). Apart from the surface forms, most of other differences are in terms of UD-based dependency parses and constituency parses of this parallel corpus, using stanza.
- Only the surface forms and morphosyntactic information is being used in this project. The parallel corpus has been created to ensure that *ONLY* morphosyntactic interpretation of the reduced register forms the basis for creation of the canonical forms.
- The above schema is *the basis* for all the subsquent steps in the pipelines of this project.
- It is used for extracting comprehensive features and feature-value pairs. This extraction is in the form of csv files, which are also used later to create visualizations suitable for publication in the ACL ARR format.
- This data has to be extracted across newspapers (Globally), and per-newspaper. 
- *ALL* features and feature-value pairs, as well as per-feature values, globally as well as per-newspaper have be to extracted and appropriate visualizations created.
- There are also length-based, punctuation marks related and tree-edit distance based features
- In addition, statistical tests etc. as given in other .md files have to calculated and visualized

### The project, at this stage, is divided into three parts/tasks.

-Each of them is about a specific broad aspect of this project about the two registers. 
- Each is meant for at least one publication for ACL ARR submission.
- A lot of work for this and the above steps has been done, but it is all mixed up due to errors at different stages.

The output has to be put in appropriate directory structure. For each task, there should be a separate directory structure, tables, features etc.

Details of each task/part are given below

## Task-1

- It is about a thorough comparison of the two registers using the schema-based extracted features, feature-values pairs, and per-feature values
- All of the above has to done for this task
- The reduced register has been studied a lot in the past and the purpose of the task is to quantitatively study the comparison and see if the insights from match those from the previous work

## Task-2

- It is about transformation of the reduced register surface forms (sentences) to the canonical register and match the final result for one sentence with the canonical register, for evaluating how well it works
- It can be thought of as being analogous to the Deep Structure to Surface Structure Transformational Grammar of Chomsky
- It has to be studied in various ways as given in other .md files, such as progressive converage of rules
- Tables and visualizations have to be created.
- This too has to be done Globally (across newspapers) and per newspaper. 

## Task 3

- It is about a thorough study of complexity and similarity of/between the two registers based not only on the surface forms, but on the features, feature-value pairs, and per-feature values.
- This has to be done bidirectionally (Reduced to Canonical and vice-versa).
- Linguistic insights will be derived from the output of this task about relative complexity of the two registers and the asymmetric similarity between them in both directions.
- It could perhaps be useful about studying the question of the linguistic interface between morphosyntax and semantics, which has been studied over the decades. 

## LaTeX files

- For each task, a separate LaTeX file, with the related tables and figures, has to be created
- Each task will have a separate directory within the LATEX directory, which is excluded from git
- It is based on ACL ARR submission format
- Only the tables and the figures have to included in the LaTeX files, with placeholder sections and text
- The main table and figures have to fit in the 8 page limit. *All the rest* has to be in the appendices
- A shared bibliography has to be used in ACL ARR style

From now, till all three tasks are completed and submitted, the main work is to do cleanup and refactoring, rearranging of the directories, files and figures, task-wise and for each task, Globally and per-newspaper and so on as given above.

A full-fledged CLI has to be created to easily rerun pipelines, for each task with all the appropriate options.

If feasible in a short time, the code can also be refactored into first the base part, and then per-task. If too complex and risky, given that only a day and half is left till submission deadline, it need not be done at present.