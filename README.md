# python-debugging

This project is based upon the AWS Python local debugging tutorial at https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-debugging-python.html

However, the AWS tutorial is not totally clear and also (as of May 20221) uses the ptvsd debugging library. ptvsd has been deprecated in favour of debugpy. This project aim to unambiguosly demonstrate step through debugging of a locally running lambda function using AWS SAM and VScode.

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.
- requirements.txt - application dependencies
- launch.json - Tells VScode how to run application and in this case how to attach to the debugger
- sonar-project.properties - SonarQube exclusions file

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

Rather than following the AWS tutorial where it tells you to create a duplicate of the project in hello_world\build use this code. AWS is trying to illustrate that in python debug code is modified production code ie. this is an inherent limitation of Python, the code need to be modified to enable debugging.

For Python, AWS SAM won't really do anything other than port forward when given `-d`, so it is up to the code itself to enable debugpy.
There isn't an easy mechanism to detect whether `-d` was given so I'm using an environment variable as a workaround.

To enable debugging in the code base you must ensure that the IS_DEBUG environment variable is set to true and uncommented in the template.yaml file. This will make that environment variable available in the SAM Docker container where your Lambda is running.

Make sure Docker is running.
```bash
#Install the dependencies:
pip install -r hello_world/requirements.txt
```

```bash
#This is the build deploy cycle. You must rebuild after any code change.
sam build --use-container  
sam local start-api -d 5890
```

Unfortunately this approach does not allow you to modify code on the fly*. Any changes require stopping the container, rebuilding and then redeploying.

**NOTE:** *It is possible to change code on the fly in the debugger by modifying code in the .aws-sam folder. However, be careful, this code is not the versioned code and any changes will be overwritten at every aws build command!!! Also the .aws-sam\build folder should be in .gitignore and so should never be committed into the code repo. ***BE WARNED!!!***

The container is now running and waiting for a debugger to attach on port 5890 after a message on port 3000. We will need to set a breakpoint in the code to halt execution:

Open the code in VScode and set a breakpoint within the lambda_handler function in app.py and after the debugpy listen and wait commands. 

Then using a browser connect to http://localhost:3000/hello
You should see "IS_DEBUG is true, waiting for debugger on 0.0.0.0:5890" in the terminal

Then from the top menu select Run->Start debugging. Click on the Python:Remote Attach tab and select SAM CLI Python Hello World.



If everything is set up correctly, VScode should highlight the code line where your breakpoint is


**NOTES:**

The details below are directly from the AWS example. they are only incuded here in case the AWS example is modified/updated.

When deploying to AWS rather than locally, using sam deploy --guided can write a config file to speed up subsequent deploys. Be aware that this config file will contain AWS account detail, _**it should never be commmitted to a repository under any circumstances!!!**_

Thanks to James Lakin


---

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
python-debugging$ sam build --use-container
```

The SAM CLI installs dependencies defined in `hello_world/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
python-debugging$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
python-debugging$ sam local start-api
python-debugging$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
python-debugging$ sam logs -n HelloWorldFunction --stack-name python-debugging --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
python-debugging$ pip install pytest pytest-mock --user
python-debugging$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name python-debugging
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
