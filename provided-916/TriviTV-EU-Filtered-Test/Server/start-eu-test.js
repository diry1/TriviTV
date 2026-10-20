import { createAppServer } from "./src/server.js";
const server = createAppServer();
server.listen(Number(process.env.PORT || 3000), "0.0.0.0", () => console.log(`TriviTV EU-filtered test: port ${server.address().port}; enter this computer's LAN IP on the TV.`));
