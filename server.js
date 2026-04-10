const express = require("express");
const http = require("http");
const socketIo = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static("public"));

let users = {};        // socket.id -> username
let messages = [];     // store messages for admin

io.on("connection", (socket) => {

  // JOIN
  socket.on("join", (username) => {
    if(!username) return;

    users[socket.id] = username;

    let joinMsg = `${username} joined the chat`;
    messages.push(joinMsg);

    io.emit("userList", Object.values(users));
    io.emit("message", joinMsg);

    sendAdminData();   // ✅ update admin
  });

  // PUBLIC MESSAGE
  socket.on("chatMessage", (msg) => {
    if(!users[socket.id] || !msg) return;

    let fullMsg = `${users[socket.id]}: ${msg}`;
    messages.push(fullMsg);

    io.emit("message", fullMsg);

    sendAdminData();   // ✅ update admin
  });

  // PRIVATE MESSAGE
  socket.on("privateMessage", ({ toUser, message }) => {
    let sender = users[socket.id];
    if(!sender || !toUser || !message) return;

    let targetId = Object.keys(users).find(
      id => users[id] === toUser
    );

    if (targetId) {
      io.to(targetId).emit("privateMessage", {
        from: sender,
        message
      });

      socket.emit("privateMessage", {
        from: "You",
        message
      });

      // store for admin
      messages.push(`(Private) ${sender} → ${toUser}: ${message}`);
    }

    sendAdminData();   // ✅ update admin
  });

  // DISCONNECT
  socket.on("disconnect", () => {
    let username = users[socket.id];

    if(username){
      let leaveMsg = `${username} left the chat`;
      messages.push(leaveMsg);

      io.emit("message", leaveMsg);
    }

    delete users[socket.id];

    io.emit("userList", Object.values(users));

    sendAdminData();   // ✅ update admin
  });

  // ✅ ADMIN DATA FUNCTION
  function sendAdminData(){
    io.emit("adminData", {
      users: Object.values(users),
      messages: messages
    });
  }

});

server.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});