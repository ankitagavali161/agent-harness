# Bedrock AgentCore — Customer Support Agent

A customer support agent built with the **Strands** SDK and deployed on **Amazon Bedrock AgentCore**.
Created from the [AgentCore Getting Started workshop](https://catalog.workshops.aws/agentcore-getting-started/).

## What it is

- **Brain:** a Strands `Agent` (`app/CustomerSupport/main.py`) using a Bedrock model
  (`app/CustomerSupport/model/load.py`) with two tools — `get_return_policy` and `get_product_info`.
- **Body:** AgentCore Runtime + Memory, declared in `agentcore/agentcore.json` and built by the
  CDK app in `agentcore/cdk/`.

## Layout

```
agentcore/              # AgentCore project config + CDK deploy stack
  agentcore.json        # runtimes + memory definition (the "order form")
  cdk/                  # CDK app that builds the AWS resources
app/CustomerSupport/    # the agent code
  main.py               # entrypoint: BedrockAgentCoreApp + Strands Agent + tools
  model/load.py         # which Bedrock model to use
  memory/session.py     # AgentCore Memory integration (semantic + episodic)
```

## Run it

Requires the [AgentCore CLI](https://www.npmjs.com/package/@aws/agentcore) (Node 22) and AWS credentials.

```bash
# set YOUR deploy target (account/region) — not included in this repo
agentcore configure

agentcore dev       # run + test locally
agentcore deploy    # build + deploy to AWS
agentcore invoke '{"prompt": "What is the return policy for audio products?"}'
```

## Not included

`agentcore/aws-targets.json` and `agentcore/.cli/` are intentionally **git-ignored** — they embed an
AWS account ID and deployed-stack ARNs. Run `agentcore configure` to generate your own.
