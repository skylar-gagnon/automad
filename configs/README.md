# Description of Configuration Parameters

The following is a description of all possible parameters for the AutoMAD configuration file.

## Necessary Parameters

These are the only parameters that need to be specified for AutoMAD to run.

| Key Word      | Type   | Description                                                      |
| ------------- | ------ | ---------------------------------------------------------------- |
| automad_path  | string | Path to the AutoMAD repo                                         |
| runtime       | string | Amount of time AutoMAD will be run for (can use 's', 'm', or 'h) |
| save_config   | bool   | If the configuration settings should be saved in run log         |
| train         | bool   | If the model will be trained during runtime                      |
| email_if_fail | bool   | If an email should be sent if an error occurs during runtime     |

## Email Parameters

These parameters only need to be set if you wish to use `email_if_fail = true`. They control how the notification of failure email gets sent. All of these appear within the `email_kwargs` settings.

| Key Word    | Type   | Description                                                  |
| ----------- | ------ | ------------------------------------------------------------ |
| sender      | string | Email address notification will be sent **from**             |
| reciever    | string | Email address notification will be sent **to**               |
| port        | int    | The port to which to connect                                 |
| smtp_server | string | The name of the remote host to which to connect              |
| password    | string | Password for sender's email (if gmail, use an app password)  |

## Generator Parameters

These parameters control how code gets generated. All of these appear within the `generator_kwargs` settings.

| Key Word     | Type   | Description                                                  |
| ------------ | ------ | ------------------------------------------------------------ |
| model_name   | string | Name of LLM to use for generation (see [Hugging Face](https://huggingface.co) for options) |
| batch_size   | int    | Number of responses the model should generate each loop       |
| device       | string | Where the model is put (either 'cuda' or 'cpu'). **Use 'cuda' if possible** |
| prompt       | string | Prompt for the LLM |
| model_kwargs | dict   | Parameters for model generation (see [here](https://huggingface.co/docs/transformers/main_classes/text_generation#generation) for all options) |

## Classifier Parameters

These parameters control the internals of the classifier module. All of these appear within the `classifier_kwargs` settings.

| Key Word            | Type   | Description                                                  |
| ------------------- | ------ | ------------------------------------------------------------ |
| template_path       | string | Path to template file (where snippet gets inserted)          |
| measure_config_path | string | Path to the xml file that controls the Measurement class     |
| max_ssh_attempts    | int    | Max number of SSH attempts before flagging snippet as an `SSH_FAILURE` |
| max_patch_attempts  | int    | Max number of times code will be compiled and patched        |
| verbose             | bool   | If internal info should be printed (number of current samples, stderr). Can help with debugging |

## Logger Parameters

These parameters control the internals of the logger module. All of these appear within the `logger_kwargs` settings.

| Key Word  | Type   | Description                                                                                     |
| --------- | ------ | ----------------------------------------------------------------------------------------------- |
| run_name  | string | Name of log directory                                                                           |
| top_n     | int    | How many spots snippets should compete for (snippets outside of the top n will not be flagged)  |
| save_data | bool   | If data (model response, processed snippet, max peak-to-peak, avg peak-to-peak) should be saved |
| verbose   | bool   | Prints time information and current cumulative flags (helpful for efficiency tuning)            |

## Training Parameters

These parameters only need to be set if you wish to use `train = true`. They control the internals of the generation module when in training mode. All of these appear within the `train_kwargs` settings.

| Key Word         | Type   | Description                                                    |
| ---------------- | ------ | -------------------------------------------------------------- |
| save_model_name  | string | Name of newly trained model                                    |
| train_model_name | string | Name of model to undergo training                              |
| ref_model_name   | string | Name of comparative model for training (needed for ODPO)       |
| make_dataset     | bool   | If a dataset of prompts needs to be made                       |
| dataset_size     | int    | If `make_dataset = true`, number of prompts in the dataset     |
| dataset_path     | string | if `make_dataset = false`, path to csv where dataset is stored |
| push_to_hub      | bool   | If model should be uploaded to Hugging Face                    |
| log_training     | bool   | If training should be logged using weights and biases (wandb)  |
| epochs           | int    | Number of training epochs                                      |