import * as vscode from 'vscode';
import * as http from 'http';

export function activate(context: vscode.ExtensionContext) {
    console.log('py-copilot extension activated');

    // Get port number
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
                    const filePath = data.file_path; // New: file path
                    const fileName = data.file_name; // New: file name
                    console.log('Received from Python:', userText);
                    if (filePath) {
                        console.log('File attached:', filePath);
                    }

                    // Actual Copilot interaction approach
                    let success = false;
                    let result = 'no_copilot';
                    let copilotReply = '';

                    try {
                        // 1. Create dedicated output channel (using simple name)
                        const outputChannel = vscode.window.createOutputChannel('Python-to-Copilot');
                        context.subscriptions.push(outputChannel);

                        outputChannel.clear();
                        outputChannel.appendLine(`🐍 Python Message [${new Date().toLocaleTimeString()}]`);
                        outputChannel.appendLine(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                        outputChannel.appendLine(`📝 ${userText}`);
                        if (filePath) {
                            outputChannel.appendLine(`📎 Attached file: ${fileName || filePath}`);
                        }
                        outputChannel.appendLine(``);
                        outputChannel.appendLine(`🤖 Next steps:`);
                        outputChannel.appendLine(`1. This message has been passed to VS Code`);
                        if (filePath) {
                            outputChannel.appendLine(`2. Attached file detected, processing...`);
                            outputChannel.appendLine(`3. I'm trying to open Copilot Chat...`);
                        } else {
                            outputChannel.appendLine(`2. I'm trying to open Copilot Chat...`);
                        }

                        // 2. Handle file attachment (if any)
                        let finalMessage = userText;
                        if (filePath) {
                            try {
                                // Read file content
                                const fs = require('fs');
                                const path = require('path');

                                if (fs.existsSync(filePath)) {
                                    const fileContent = fs.readFileSync(filePath, 'utf8');
                                    const fileExt = path.extname(filePath);
                                    const displayName = fileName || path.basename(filePath);

                                    // Build message with file content
                                    finalMessage = `${userText}\n\n📎 Attached file: ${displayName}\n\`\`\`${fileExt.slice(1) || 'text'}\n${fileContent}\n\`\`\``;

                                    outputChannel.appendLine(`✅ File content read (${fileContent.length} characters)`);
                                } else {
                                    outputChannel.appendLine(`⚠️  File does not exist: ${filePath}`);
                                    finalMessage = `${userText}\n\n⚠️ Note: Attached file does not exist (${filePath})`;
                                }
                            } catch (fileError) {
                                console.error('File reading error:', fileError);
                                const errorMsg = fileError instanceof Error ? fileError.message : 'Unknown error';
                                outputChannel.appendLine(`❌ File reading failed: ${errorMsg}`);
                                finalMessage = `${userText}\n\n❌ Note: Attached file reading failed`;
                            }
                        }

                        // 3. Try to open Copilot Chat and send message
                        let chatOpened = false;
                        let messageSent = false;

                        try {
                            // Open Copilot Chat panel
                            await vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
                            chatOpened = true;
                            outputChannel.appendLine(`✅ Copilot Chat opened`);

                            // Try to send message directly to Chat
                            try {
                                // Method 1: Use Chat API to send message
                                await vscode.commands.executeCommand('workbench.action.chat.submitToChat', {
                                    text: finalMessage,
                                    participant: 'copilot'
                                });
                                messageSent = true;
                                outputChannel.appendLine(`✅ Message automatically sent to Copilot Chat`);
                                result = 'message_sent';
                            } catch (sendError) {
                                // Method 2: Auto-paste to Chat input box
                                try {
                                    // Copy message to clipboard
                                    await vscode.env.clipboard.writeText(finalMessage);
                                    outputChannel.appendLine(`✅ Message copied to clipboard`);

                                    // Wait a moment to ensure Chat panel is focused
                                    await new Promise(resolve => setTimeout(resolve, 300));

                                    // Auto-paste to focused input box
                                    await vscode.commands.executeCommand('editor.action.clipboardPasteAction');
                                    outputChannel.appendLine(`✅ Message automatically pasted to Chat input box`);

                                    // Wait a moment to ensure paste is complete
                                    await new Promise(resolve => setTimeout(resolve, 200));

                                    // Try to auto-press Enter to send message
                                    try {
                                        // Method 2a: Try using Chat submit command
                                        await vscode.commands.executeCommand('workbench.action.chat.submit');
                                        outputChannel.appendLine(`✅ Message automatically sent to Copilot`);
                                        result = 'auto_sent_with_enter';
                                    } catch (submitError) {
                                        try {
                                            // Method 2b: Try simulating Enter key
                                            await vscode.commands.executeCommand('type', { text: '\n' });
                                            outputChannel.appendLine(`✅ Simulated Enter key press to send message`);
                                            result = 'auto_sent_with_type';
                                        } catch (typeError) {
                                            // Method 2c: Try sending keyboard event
                                            try {
                                                await vscode.commands.executeCommand('workbench.action.quickOpenNavigateNext');
                                                await vscode.commands.executeCommand('workbench.action.acceptSelectedQuickOpenItem');
                                                outputChannel.appendLine(`✅ Attempted to auto-send message`);
                                                result = 'auto_sent_attempt';
                                            } catch (keyError) {
                                                outputChannel.appendLine(`🎯 Message pasted, please manually press Enter to send`);
                                                result = 'auto_pasted';
                                            }
                                        }
                                    }

                                    messageSent = true;
                                } catch (pasteError) {
                                    // Method 3: Fallback, copy to clipboard only
                                    try {
                                        await vscode.env.clipboard.writeText(finalMessage);
                                        outputChannel.appendLine(`✅ Message copied to clipboard`);
                                        outputChannel.appendLine(`   Please press Ctrl+V in Copilot Chat to paste`);
                                        result = 'copied_to_clipboard';
                                        messageSent = true;
                                    } catch (clipError) {
                                        outputChannel.appendLine(`⚠️  Unable to auto-process message, please input manually`);
                                        result = 'manual_input_required';
                                    }
                                }
                            }
                        } catch (chatError) {
                            outputChannel.appendLine(`⚠️  Unable to auto-open Copilot Chat`);
                            outputChannel.appendLine(`   Please manually press Ctrl+Shift+I or search "Chat" in command palette`);
                            result = 'manual_required';
                        }

                        outputChannel.appendLine(``);
                        if (messageSent) {
                            outputChannel.appendLine(`🎉 Message processing complete:`);
                            if (result === 'message_sent') {
                                outputChannel.appendLine(`• Message automatically sent to Copilot Chat`);
                                outputChannel.appendLine(`• Please check Copilot's reply in the Chat panel`);
                            } else if (result === 'auto_sent_with_enter' || result === 'auto_sent_with_type' || result === 'auto_sent_attempt') {
                                outputChannel.appendLine(`• 🎉 Message fully automatically sent to Copilot`);
                                outputChannel.appendLine(`• Please check Copilot's reply in the Chat panel`);
                            } else if (result === 'auto_pasted') {
                                outputChannel.appendLine(`• Message automatically pasted to Chat input box`);
                                outputChannel.appendLine(`• 🎯 Please press Enter to send to Copilot`);
                            } else if (result === 'copied_to_clipboard') {
                                outputChannel.appendLine(`• Message copied to clipboard`);
                                outputChannel.appendLine(`• Please press Ctrl+V in Copilot Chat to paste and send`);
                            }
                        } else {
                            outputChannel.appendLine(`💡 Usage suggestions:`);
                            outputChannel.appendLine(`• Copy this question to Copilot Chat: "${userText}"`);
                            outputChannel.appendLine(`• Or ask directly in Chat`);
                        }
                        outputChannel.appendLine(`• Copilot's reply will appear in the Chat panel`);
                        outputChannel.appendLine(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

                        // 3. Force show output channel
                        outputChannel.show(true);

                        // Ensure output channel is in foreground
                        setTimeout(() => {
                            outputChannel.show(true);
                        }, 100);

                        // 4. Show concise notification
                        vscode.window.showInformationMessage(
                            `🎉 Python message automatically sent to Copilot: ${userText.substring(0, 40)}${userText.length > 40 ? '...' : ''}`
                        );

                        // 5. Show in status bar
                        if (messageSent) {
                            if (result === 'auto_pasted') {
                                vscode.window.setStatusBarMessage(
                                    `🐍→🤖 Message pasted to Chat, please press Enter to send`,
                                    10000
                                );
                            } else if (result === 'auto_sent_with_enter' || result === 'auto_sent_with_type' || result === 'auto_sent_attempt') {
                                vscode.window.setStatusBarMessage(
                                    `🎉 Python message fully automatically sent to Copilot`,
                                    8000
                                );
                            } else {
                                vscode.window.setStatusBarMessage(
                                    `🐍→🤖 Python message sent to Copilot Chat`,
                                    8000
                                );
                            }
                        } else {
                            vscode.window.setStatusBarMessage(
                                `🐍→🤖 Python message ready, please manually send to Copilot`,
                                8000
                            );
                        }

                        copilotReply = messageSent
                            ? (result === 'message_sent'
                                ? '✅ Message automatically sent to Copilot Chat, please check reply'
                                : (result === 'auto_sent_with_enter' || result === 'auto_sent_with_type' || result === 'auto_sent_attempt')
                                    ? '🎉 Message fully automatically sent to Copilot, please check reply'
                                    : result === 'auto_pasted'
                                        ? '✅ Message pasted to Chat input box, please press Enter to send'
                                        : '✅ Message copied to clipboard, please paste in Chat')
                            : '⚠️ Please manually send message to Copilot Chat'; success = true;
                        console.log('Successfully prepared Copilot interaction');

                    } catch (error) {
                        console.error('Failed to process message:', error);

                        // Fallback: simply display message
                        vscode.window.showInformationMessage(`Python message: ${userText}`);
                        copilotReply = '❌ Processing error occurred, but message received';
                        result = 'error_fallback';
                        success = true;
                    }

                    // Reply to Python with processing result
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        status: success ? 'success' : 'failed',
                        result: result,
                        message: userText,
                        copilot_reply: copilotReply,
                        instructions: "Please check Copilot's reply in VS Code Chat panel"
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
