(function() {
    var ws = null;
    var connected = false;
    var historyItems = [];

    var serverUrl;
    var connectionStatus;
    var sendMessage;

    var historyList;
    var connectButton;
    var disconnectButton;
    var sendButton;

    const max = 999999;
    const min = 111111;

    function randInt() {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    document.getElementById('userName').value =`User${randInt()}`;

    var open = function() {
        var url = 'ws://' + serverUrl.val() + ':8765';
        ws = new WebSocket(url);
        ws.onopen = onOpen;
        ws.onclose = onClose;
        ws.onmessage = onMessage;
        ws.onerror = onError;

        connectionStatus.text('CONNECTING ...');
        serverUrl.attr('disabled', 'disabled');
        connectButton.hide();
        disconnectButton.show();
    };

    var close = function() {
        if (ws) {
            console.log('DISCONNECTING...');
            ws.close();
        }
    };

    var reset = function() {
        connected = false;
        connectionStatus.text('NOT_CONNECTED');

        serverUrl.removeAttr('disabled');
        connectButton.show();
        disconnectButton.hide();
        sendMessage.attr('disabled', 'disabled');
        sendButton.attr('disabled', 'disabled');
    };

    var clearLog = function() {
        $('#messages').html('');
    };

    var onOpen = function() {
        console.log('CONNECTED: ' + serverUrl.val());
        connected = true;
        connectionStatus.text('CONNECTED');
        sendMessage.removeAttr('disabled');
        sendButton.removeAttr('disabled');

        ws.send(JSON.stringify({'type':'user_joined', 'payload':$('#userName').val()}));
    };

    var onClose = function() {
        console.log('NOT_CONNECTED: ' + serverUrl.val());
        ws = null;
        reset();
    };

    var onMessage = function(event) {
        var data = JSON.parse(event.data);
        if (data['type'] === 'welcome') {
            console.log(data)
            addMessage(`[SERVER] ${data['message']}`);
            document.getElementById('tid').value = data['client_address'];
            document.getElementById('serverinfo').innerHTML = `<label>server version: </label>${data['server_version']}<br><label>server brand: </label>${data['server_brand']}<br><label>server type: </label>${data['server_type']}<br><label>server name: </label>${data['server_appn']}<br><label>server UUID:</label><br>${data['server_uuid']}`;
            if (data['server_type'] !== 'chat') {
                console.log('invalid server')
                window.alert(`${data['server_appn']} is not a server of type 'chat'. You will now be disconnected.`);
                close();
                console.log('NOT_CONNECTED: ' + serverUrl.val());
                ws = null;
                reset();
            }
        } else if (data['type'] === 'chat') {
            if (data['sender'] !== document.getElementById('tid').value) {
                addMessage(`[${data['user']}] ${data['payload']}`);
            }
        } else if (data['type'] === 'user_joined') {
            addMessage(`[SERVER] ${data['payload']} joined`);
        } else if (data['type'] === 'user_left') {
            if (data['sender'] !== document.getElementById('tid').value) {
                addMessage(`[SERVER] ${data['payload']} left ${data['server_appn']}`);
            }
        } else {
            addMessage(`Server sent unknown message type: ${data['type']}`);
        }
    };

    var onError = function(event) {
        alert(event.type);
    };

    var addMessage = function(data, type) {
        var msg = $('<pre>').text(data);
        if (type === 'SENT') {
            msg.addClass('sent');
        }
        var messages = $('#messages');
        messages.append(msg);

        var msgBox = messages.get(0);
        while (msgBox.childNodes.length > 1000) {
            msgBox.removeChild(msgBox.firstChild);
        }
        msgBox.scrollTop = msgBox.scrollHeight;
    };

    var guid = function() {
        function s4() {
            return Math.floor((1 + Math.random()) * 0x10000)
                .toString(16)
                .substring(1);
        }
        return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
    };

    WebSocketClient = {
        init: function() {
            serverUrl = $('#serverUrl');
            connectionStatus = $('#connectionStatus');
            sendMessage = $('#sendMessage');
            connectButton = $('#connectButton');
            disconnectButton = $('#disconnectButton');
            sendButton = $('#sendButton');
            connectButton.click(function(e) {
                close();
                open();
            });

            disconnectButton.click(function(e) {
                ws.send(JSON.stringify({'type':'user_left', 'payload':$('#userName').val()}));
                close();
            });

            sendButton.click(function(e) {
                var msg = $('#sendMessage').val();
                addMessage(`[${$('#userName').val()}] ${msg}`, 'SENT');
                ws.send(JSON.stringify({'type':'chat', 'payload':msg, 'user':$('#userName').val()}));
            });

            $('#clearMessage').click(function(e) {
                clearLog();
            });

            serverUrl.keydown(function(e) {
                if (e.which === 13) {
                    connectButton.click();
                }
            });

            var isCtrl;
            sendMessage.keyup(function(e) {
                if (e.which === 17) {
                    isCtrl = false;
                }
            }).keydown(function(e) {
                if (e.which === 17) {
                    isCtrl = true;
                }
                if (e.which === 13 && isCtrl === true) {
                    sendButton.click();
                    return false;
                }
            });
        }
    };
})();

var WebSocketClient;

$(function() {
    WebSocketClient.init();
});
