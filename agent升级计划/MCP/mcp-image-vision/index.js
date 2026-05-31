import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import OpenAI from "openai";
import { readFileSync } from "fs";

const args = process.argv.slice(2);
const API_KEY = args.find(a => a.startsWith("--api-key="))?.split("=")[1] || process.env.ZHIPU_API_KEY;
const MODEL = args.find(a => a.startsWith("--model="))?.split("=")[1] || process.env.VISION_MODEL || "GLM-4V-Flash";
const BASE_URL = "https://open.bigmodel.cn/api/paas/v4";

if (!API_KEY) {
  console.error("ZHIPU_API_KEY is required (use --api-key=xxx or set env)");
  process.exit(1);
}

const client = new OpenAI({ apiKey: API_KEY, baseURL: BASE_URL });

const server = new Server(
  { name: "image-vision", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "describe_image",
      description: "分析图片内容并返回详细描述。支持截图、照片等常见格式。可以用中文或英文提问。",
      inputSchema: {
        type: "object",
        properties: {
          image_path: { type: "string", description: "图片文件的绝对路径" },
          question: { type: "string", description: "要问的问题（可选），默认返回完整描述", default: "请详细描述这张图片的内容" }
        },
        required: ["image_path"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "describe_image") {
    try {
      const { image_path, question } = request.params.arguments;
      const imageBuffer = readFileSync(image_path);
      const base64 = imageBuffer.toString("base64");
      const ext = image_path.split(".").pop().toLowerCase();
      const mime = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp", gif: "image/gif" }[ext] || "image/png";

      const response = await client.chat.completions.create({
        model: MODEL,
        messages: [{
          role: "user",
          content: [
            { type: "image_url", image_url: { url: `data:${mime};base64,${base64}` } },
            { type: "text", text: question || "请详细描述这张图片的内容" }
          ]
        }],
        stream: false
      });

      return { content: [{ type: "text", text: response.choices[0].message.content }] };
    } catch (e) {
      return { content: [{ type: "text", text: `错误: ${e.message}` }], isError: true };
    }
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
