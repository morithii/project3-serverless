import dax from "@amazon-dax-sdk/lib-dax";

const { DaxDocument } = dax;

// Created once per container: the DAX connection is set up on the first call and reused
const client = new DaxDocument({ endpoint: process.env.DAX_ENDPOINT, region: process.env.AWS_REGION });
const TABLE_NAME = process.env.TABLE_NAME;

const response = (statusCode, body) => ({
  statusCode,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const handler = async (event) => {
  const orderId = event.pathParameters?.orderId ?? event.orderId;
  if (!orderId) {
    return response(400, { message: "orderId is required" });
  }

  const start = performance.now();
  const result = await client.query({
    TableName: TABLE_NAME,
    KeyConditionExpression: "orderId = :o",
    ExpressionAttributeValues: { ":o": orderId },
  });
  const daxMs = Number((performance.now() - start).toFixed(2));

  console.log(JSON.stringify({ message: "DAX query", orderId, daxMs, count: result.Items?.length ?? 0 }));

  if (!result.Items || result.Items.length === 0) {
    return response(404, { message: "Order not found", daxMs });
  }

  return response(200, {
    orderId,
    source: "dax",
    daxMs,
    items: result.Items.map(({ itemId, productId, quantity, price }) => ({ itemId, productId, quantity, price })),
  });
};
