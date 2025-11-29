import * as vscode from 'vscode';
import * as http from 'http';

export function activate(context: vscode.ExtensionContext) {
    console.log('py-copilot extension activated');

    const config = vscode.workspace.getConfiguration('py-copilot');
    const port = config.get<number>('serverPort', 12345);

    const server = http.createServer(async (req, res) => {
        console.log(`Received ${req.method} request to ${req.url}`);

        if (req.method === 'POST' && req.url === '/message') {
            let body = '';
            req.on('data', chunk => (body += chunk.toString()));
            req.on('end', async () => {
                try {
                    const data = JSON.parse(body);
                    const userText = data.text;
                    const filePath = data.file_path;
                    const fileName = data.file_name;
                    console.log('Received from Python:', userText);
                    if (filePath) {
                        console.log('File attached:', filePath);
                    }

                    let success = false;
                    let result = 'no_copilot';
                    let copilotReply = '';

                    try {
                        const outputChannel = vscode.window.createOutputChannel('Python-to-Copilot');
                        context.subscriptions.push(outputChannel);

                        outputChannel.clear();
                        outputChannel.appendLine(`Message: ${userText}`);
                        if (filePath) {
                            outputChannel.appendLine(`File: ${fileName || filePath}`);
                        }

                        let finalMessage = userText;
                        if (filePath) {
                            try {
                                const fs = require('fs');
                                const path = require('path');

                                if (fs.existsSync(filePath)) {
                                    const fileContent = fs.readFileSync(filePath, 'utf8');
                                    const fileExt = path.extname(filePath);
                                    const displayName = fileName || path.basename(filePath);
                                    finalMessage = `${userText}\n\nFile: ${displayName}\n\`\`\`${fileExt.slice(1) || 'text'}\n${fileContent}\n\`\`\``;
                                    outputChannel.appendLine(`File loaded: ${fileContent.length} chars`);
                                } else {
                                    finalMessage = `${userText}\n\nFile not found: ${filePath}`;
                                }
                            } catch (e) {
                                console.error('File error:', e);
                                finalMessage = `${userText}\n\nFile read error`;
                            }
                        }

                        let chatOpened = false;
                        let messageSent = false;

                        try {
                            await vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
                            chatOpened = true;
                            outputChannel.appendLine('Chat opened');

                            try {
                                await vscode.commands.executeCommand('workbench.action.chat.submitToChat', {
                                    text: finalMessage,
                                    participant: 'copilot'
                                });
                                messageSent = true;
                                outputChannel.appendLine('Message sent to Chat');
                                result = 'message_sent';
                            } catch (e) {
                                await vscode.env.clipboard.writeText(finalMessage);
                                outputChannel.appendLine('Message copied to clipboard, paste in Chat');
                                result = 'copied';
                                messageSent = true;
                            }
                        } catch (e) {
                            outputChannel.appendLine('Failed to open chat, check manually');
                            result = 'manual_required';
                        }

                        outputChannel.show();

                        if (messageSent) {
                            vscode.window.showInformationMessage(`Message sent: ${userText.substring(0, 30)}...`);
                        } else {
                            vscode.window.showWarningMessage('Please open Copilot Chat manually');
                        }

                        copilotReply = messageSent ? 'Message sent to chat' : 'Please send manually';
                        success = true;

                    } catch (error) {
                        console.error('Error:', error);
                        vscode.window.showInformationMessage(`Python message: ${userText}`);
                        copilotReply = 'Error occurred, but message received';
                        result = 'error';
                        success = true;
                    }

                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        status: success ? 'success' : 'failed',
                        result: result,
                        message: userText,
                        copilot_reply: copilotReply
                    }));
                } catch (e) {
                    console.error('Error processing request:', e);
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Invalid request format' }));
                }
            });
        } else {
            res.writeHead(404);
            res.end();
        }
    });

    server.listen(port, () => {
        console.log(`HTTP server listening on port ${port}`);
    });

    context.subscriptions.push({
        dispose() {
            server.close();
        },
    });
}

export function deactivate() { }
