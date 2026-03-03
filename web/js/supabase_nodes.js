/**
 * ComfyUI-Supabase-Power Frontend Extensions
 *
 * Provides WebSocket handlers for Realtime notifications
 * and UI enhancements for Supabase nodes.
 */

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// Store active realtime subscriptions
const realtimeSubscriptions = new Map();

/**
 * Register Supabase node UI extensions
 */
app.registerExtension({
    name: "Comfy.SupabasePower",

    async setup() {
        console.log("[SupabasePower] Extension loaded");

        // Listen for workflow execution events
        api.addEventListener("execution_start", ({ detail }) => {
            console.log("[SupabasePower] Workflow started:", detail);
        });

        api.addEventListener("execution_success", ({ detail }) => {
            console.log("[SupabasePower] Workflow completed:", detail);
        });
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Add visual indicators for Supabase nodes
        if (nodeData.category?.startsWith("Supabase/")) {
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                if (originalOnNodeCreated) {
                    originalOnNodeCreated.apply(this, arguments);
                }

                // Add a subtle indicator for Supabase nodes
                this.color = "#1e3a2f";  // Dark green tint
                this.bgcolor = "#1a1a2e";  // Dark blue-ish background
            };
        }

        // Special handling for connection node
        if (nodeData.name === "SupabaseConnection") {
            const originalOnExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(message) {
                if (originalOnExecuted) {
                    originalOnExecuted.apply(this, arguments);
                }

                // Update node appearance based on connection status
                const output = message?.output;
                if (output) {
                    if (output.error && output.error[0]) {
                        this.color = "#3a1e1e";  // Red tint for error
                        this.boxcolor = "#ff4444";
                    } else if (output.is_service_role && output.is_service_role[0]) {
                        this.color = "#3a2e1e";  // Orange tint for service role
                        this.boxcolor = "#ffaa44";
                    } else {
                        this.color = "#1e3a2f";  // Green for success
                        this.boxcolor = "#44ff44";
                    }
                    this.setDirtyCanvas(true, true);
                }
            };
        }

        // Special handling for Subscribe node - show connection status
        if (nodeData.name === "SupabaseSubscribe") {
            const originalOnExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(message) {
                if (originalOnExecuted) {
                    originalOnExecuted.apply(this, arguments);
                }

                const output = message?.output;
                if (output?.status) {
                    const status = output.status[0];
                    if (status === "subscribed") {
                        this.boxcolor = "#44ff44";
                    } else if (status === "error") {
                        this.boxcolor = "#ff4444";
                    }
                    this.setDirtyCanvas(true, true);
                }
            };
        }

        // Special handling for Upload node - show progress
        if (nodeData.name === "SupabaseUpload") {
            const originalOnExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(message) {
                if (originalOnExecuted) {
                    originalOnExecuted.apply(this, arguments);
                }

                const output = message?.output;
                if (output) {
                    if (output.success && output.success[0]) {
                        this.boxcolor = "#44ff44";
                        // Show URL in node title temporarily
                        if (output.public_url && output.public_url[0]) {
                            const url = output.public_url[0];
                            const shortUrl = url.length > 40 ? url.substring(0, 40) + "..." : url;
                            this.title = `Upload ✓ ${shortUrl}`;
                        }
                    } else {
                        this.boxcolor = "#ff4444";
                        this.title = "Upload ✗ Error";
                    }
                    this.setDirtyCanvas(true, true);

                    // Reset title after delay
                    setTimeout(() => {
                        this.title = nodeData.display_name || "Supabase Upload";
                        this.setDirtyCanvas(true, true);
                    }, 5000);
                }
            };
        }
    },

    /**
     * Add context menu options for Supabase nodes
     */
    nodeCreated(node) {
        if (node.comfyClass?.startsWith("Supabase")) {
            const originalGetExtraMenuOptions = node.getExtraMenuOptions;

            node.getExtraMenuOptions = function(_, options) {
                if (originalGetExtraMenuOptions) {
                    originalGetExtraMenuOptions.apply(this, arguments);
                }

                // Add Supabase-specific menu options
                options.push(null);  // Separator

                options.push({
                    content: "📖 Supabase Docs",
                    callback: () => {
                        window.open("https://supabase.com/docs", "_blank");
                    }
                });

                if (node.comfyClass === "SupabaseConnection") {
                    options.push({
                        content: "🔧 Open Supabase Dashboard",
                        callback: () => {
                            // Try to extract URL from widget
                            const urlWidget = node.widgets?.find(w => w.name === "url");
                            if (urlWidget?.value) {
                                const projectUrl = urlWidget.value.replace(".supabase.co", ".supabase.com");
                                window.open(projectUrl, "_blank");
                            } else {
                                window.open("https://supabase.com/dashboard", "_blank");
                            }
                        }
                    });
                }
            };
        }
    }
});

/**
 * Realtime WebSocket Manager
 * Handles connections to Supabase Realtime for live updates
 */
class RealtimeManager {
    constructor() {
        this.channels = new Map();
        this.messageHandlers = new Map();
    }

    /**
     * Register a handler for realtime messages
     */
    onMessage(channelName, handler) {
        if (!this.messageHandlers.has(channelName)) {
            this.messageHandlers.set(channelName, []);
        }
        this.messageHandlers.get(channelName).push(handler);
    }

    /**
     * Dispatch message to registered handlers
     */
    dispatch(channelName, payload) {
        const handlers = this.messageHandlers.get(channelName) || [];
        handlers.forEach(handler => {
            try {
                handler(payload);
            } catch (e) {
                console.error("[SupabasePower] Handler error:", e);
            }
        });
    }

    /**
     * Clean up all subscriptions
     */
    cleanup() {
        this.channels.forEach((channel, name) => {
            try {
                channel.unsubscribe();
            } catch (e) {
                console.warn("[SupabasePower] Cleanup error:", e);
            }
        });
        this.channels.clear();
        this.messageHandlers.clear();
    }
}

// Global realtime manager instance
window.supabaseRealtimeManager = new RealtimeManager();

console.log("[SupabasePower] Frontend extension initialized");
