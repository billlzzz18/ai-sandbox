/**
 * Master tool map for the AI Agent Sandbox.
 * This file exports all available tools that agents can use.
 */

import fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export const MASTER_TOOL_MAP = {
  // File system tools
  read_file: (filePath) => {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      return { success: true, content };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  write_file: (filePath, content) => {
    try {
      fs.writeFileSync(filePath, content, 'utf8');
      return { success: true, message: "File written successfully" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  delete_file: (filePath) => {
    try {
      fs.unlinkSync(filePath);
      return { success: true, message: "File deleted successfully" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Code execution tool
  execute_code: async (language, code) => {
    try {
      let command;
      switch (language.toLowerCase()) {
        case 'python':
        case 'python3':
          command = `python3 -c "${code.replace(/"/g, '\\"')}"`;
          break;
        case 'bash':
        case 'shell':
          command = `bash -c "${code.replace(/"/g, '\\"')}"`;
          break;
        case 'node':
        case 'javascript':
          command = `node -e "${code.replace(/"/g, '\\"')}"`;
          break;
        default:
          return { success: false, error: `Unsupported language: ${language}` };
      }

      const { stdout, stderr } = await execAsync(command);
      return {
        success: true,
        output: stdout,
        error: stderr || null
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // VS Code integration
  open_in_vscode: (filePath) => {
    try {
      // This would typically open in VS Code, but for now we'll just check if file exists
      const exists = fs.existsSync(filePath);
      if (exists) {
        return { success: true, message: `File ${filePath} exists and would be opened in VS Code` };
      } else {
        return { success: false, error: `File ${filePath} does not exist` };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Web search (stub implementation)
  search: (query) => {
    console.log(`[STUB] Web search called with query: ${query}`);
    return {
      success: true,
      message: `Search results for "${query}" (stub implementation)`,
      results: [
        { title: "Sample Result 1", url: "https://example.com/1", snippet: "This is a sample search result." },
        { title: "Sample Result 2", url: "https://example.com/2", snippet: "Another sample search result." }
      ]
    };
  },

  // Legacy tools (keeping for compatibility)
  write_python: (code) => {
    console.log(`[STUB] write_python called with: ${code}`);
    return { success: true, message: "Python code written (stub)" };
  },

  api_stubs: (endpoint) => {
    console.log(`[STUB] api_stubs called with: ${endpoint}`);
    return { success: true, message: "API stub created (stub)" };
  }
};

export default MASTER_TOOL_MAP;