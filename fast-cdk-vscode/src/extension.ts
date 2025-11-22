import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
  console.log('Activating extension...');
  const textxExtension = vscode.extensions.getExtension("textX.textX");
  if (textxExtension && !textxExtension.isActive) { textxExtension.activate(); }
}

export async function deactivate(): Promise<void> {
  console.log('Deactivating extension...');
}