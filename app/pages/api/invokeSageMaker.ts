import { NextApiRequest, NextApiResponse } from 'next';
import { SageMakerRuntimeClient, InvokeEndpointCommand } from '@aws-sdk/client-sagemaker-runtime';
import { TextDecoder } from 'util';

const sagemakerClient = new SageMakerRuntimeClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).end();
  }

  const payload = {
    inputs: req.body.inputs,
  };

  const params = {
    Body: JSON.stringify(payload),
    EndpointName: 'your-huggingface-llama2-endpoint',
    ContentType: 'application/json',
  };

  const command = new InvokeEndpointCommand(params);

  try {
    const result = await sagemakerClient.send(command);
    const responsePayload = JSON.parse(new TextDecoder().decode(result.Body));
    res.status(200).json(responsePayload);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to invoke SageMaker endpoint.' });
  }
}
