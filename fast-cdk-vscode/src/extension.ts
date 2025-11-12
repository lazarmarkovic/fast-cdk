import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
  console.log('Activating extension...');
}

export async function deactivate(): Promise<void> {
  console.log('Deactivating extension...');
}