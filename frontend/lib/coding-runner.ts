import { obj, rows } from "./data";

export interface CodingRun {
  outputs: unknown[];
  error?: string;
}

// The opaque-origin frame owns a worker; its CSP prohibits network and imports.
export const CODING_FRAME = `<!doctype html>
<script>
onmessage = (event) => {
  const port = event.ports[0];
  if (!port) return;
  const workerSource = \`onmessage=async(event)=>{try{
    const {code,inputs}=event.data;
    const run=new Function("input",code+"\\\\nreturn solve(input);");
    const outputs=[];
    for(const input of inputs) outputs.push(await run(input));
    const encoded=JSON.stringify(outputs);
    if(!encoded || encoded.length>200000)throw new Error("Output is not bounded JSON.");
    postMessage({outputs:JSON.parse(encoded)});
  }catch(error){postMessage({outputs:[],error:String(error.message||error).slice(0,500)});}}\`;
  const url = URL.createObjectURL(new Blob([workerSource],{type:"text/javascript"}));
  const worker = new Worker(url);
  URL.revokeObjectURL(url);
  const timer=setTimeout(()=>{worker.terminate();port.postMessage({outputs:[],error:"Execution exceeded 3 seconds."});},3000);
  worker.onmessage=event=>{clearTimeout(timer);worker.terminate();port.postMessage(event.data);};
  worker.onerror=()=>{clearTimeout(timer);worker.terminate();port.postMessage({outputs:[],error:"Isolated execution failed."});};
  worker.postMessage(event.data);
};
</script>`;

export function runCoding(
  code: string,
  testCases: unknown,
): Promise<CodingRun> {
  if (code.length > 20000)
    return Promise.resolve({
      outputs: [],
      error: "Code exceeds 20,000 characters.",
    });
  const inputs = rows(testCases).map((test) => test.input);
  if (inputs.length > 12 || JSON.stringify(inputs).length > 100000)
    return Promise.resolve({
      outputs: [],
      error: "Fixture collection exceeds the runner limit.",
    });
  return new Promise((resolve) => {
    const frame = document.createElement("iframe");
    frame.setAttribute("sandbox", "allow-scripts");
    frame.setAttribute("aria-hidden", "true");
    frame.hidden = true;
    const channel = new MessageChannel();
    const finish = (result: CodingRun) => {
      clearTimeout(timeout);
      channel.port1.close();
      channel.port2.close();
      frame.remove();
      resolve(result);
    };
    const timeout = setTimeout(
      () =>
        finish({
          outputs: [],
          error: "Runner did not respond within 5 seconds.",
        }),
      5000,
    );
    channel.port1.onmessage = (event: MessageEvent<unknown>) => {
      const data = obj(event.data);
      finish({
        outputs: Array.isArray(data.outputs) ? data.outputs : [],
        ...(typeof data.error === "string" ? { error: data.error } : {}),
      });
    };
    frame.onload = () =>
      frame.contentWindow?.postMessage({ code, inputs }, "*", [channel.port2]);
    frame.src = "/coding-sandbox";
    document.body.append(frame);
  });
}
