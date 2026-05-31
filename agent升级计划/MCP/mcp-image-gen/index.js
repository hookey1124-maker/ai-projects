import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { writeFileSync, mkdirSync, readFileSync } from "fs";
import { extname } from "path";

const args = process.argv.slice(2);
const API_KEY = args.find(a => a.startsWith("--api-key="))?.split("=")[1] || process.env.MAIZI_API_KEY;
const BASE_URL = "https://www.maizitech.cn/v1";

if (!API_KEY) {
  console.error("MAIZI_API_KEY is required (use --api-key=xxx or set env)");
  process.exit(1);
}

const MODELS = [
  "gpt-image-2 (￥0.06~0.105/次, 1K/2K/4K)",
  "nano-banana-fast (￥0.06/次, 1K)",
  "gpt-image-2-official (￥0.053~11.43/次, 1K/2K/4K)",
  "nano-banana-2 (￥0.12/次, 1K/2K/4K)",
  "nano-banana-pro (￥0.18/次, 1K/2K/4K)"
];

const MODEL_IDS = ["gpt-image-2", "nano-banana-fast", "gpt-image-2-official", "nano-banana-2", "nano-banana-pro"];

const server = new Server(
  { name: "image-gen", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "generate_image",
      description: `调用麦子AI生成图片。可用模型: ${MODELS.join(", ")}。支持传参考图进行图生图/局部重绘。`,
      inputSchema: {
        type: "object",
        properties: {
          prompt: { type: "string", description: "图片描述（中文或英文）" },
          model: { type: "string", description: "模型名称", default: "gpt-image-2" },
          size: { type: "string", description: "图片尺寸，如 4k, 1:1, 16:9, 4:3", default: "4k" },
          reference_image: { type: "string", description: "参考图绝对路径（可选）。提供后可基于参考图生成，保持产品结构不变。" },
          strength: { type: "number", description: "参考图控制强度 0-1。越低越忠实参考图，越高越自由。默认 0.5。", default: 0.5 }
        },
        required: ["prompt"]
      }
    }
  ]
}));

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const pollTask = async (taskId) => {
  for (let i = 0; i < 30; i++) {
    const r = await fetch(`${BASE_URL}/tasks/${taskId}`, {
      headers: { "Authorization": `Bearer ${API_KEY}` }
    });
    const j = await r.json();
    if (j.status === "completed") return j;
    if (j.status === "failed") throw new Error(j.error_msg || "任务失败");
    await sleep(2000);
  }
  throw new Error("任务超时，请重试");
};

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "generate_image") {
    try {
      const { prompt, model = "gpt-image-2", size = "4k", reference_image, strength = 0.5 } = request.params.arguments;

      const body = { model, prompt, n: 1, size };

      if (reference_image) {
        const imgBuffer = readFileSync(reference_image);
        const b64 = imgBuffer.toString("base64");
        const ext = extname(reference_image).slice(1) || "png";
        body.image = `data:image/${ext};base64,${b64}`;
        body.strength = strength;
      }

      const resp = await fetch(`${BASE_URL}/images/generations`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      const json = await resp.json();

      if (json.error) {
        return { content: [{ type: "text", text: `API错误: ${json.error.message || JSON.stringify(json.error)}` }], isError: true };
      }

      const taskId = json.data?.[0]?.task_id;
      if (!taskId) {
        return { content: [{ type: "text", text: `返回异常: ${JSON.stringify(json)}` }], isError: true };
      }

      const result = await pollTask(taskId);

      const resultUrl = result.result_urls?.[0];
      if (!resultUrl) {
        return { content: [{ type: "text", text: `任务完成但无图片: ${JSON.stringify(result)}` }], isError: true };
      }

      const imgUrl = resultUrl.startsWith("http") ? resultUrl : `https://www.maizitech.cn${resultUrl}`;
      const imgResp = await fetch(imgUrl);
      const buffer = Buffer.from(await imgResp.arrayBuffer());

      const dir = process.env.USERPROFILE + "/Desktop/ai-images";
      mkdirSync(dir, { recursive: true });
      const filename = `gen_${Date.now()}.png`;
      const filepath = `${dir}/${filename}`;
      writeFileSync(filepath, buffer);

      const refInfo = reference_image ? `\n参考图: ${reference_image}` : "";
      return { content: [{ type: "text", text: `生成成功！已保存到: ${filepath}\n模型: ${model}\n费用: ￥${result.cost}\n提示词: ${prompt}${refInfo}` }] };
    } catch (e) {
      return { content: [{ type: "text", text: `错误: ${e.message}` }], isError: true };
    }
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
