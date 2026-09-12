-- Arch Theme Manager
-- Neovim runtime integration.
--
-- This file:
--   1. Loads the generated Neovim theme.
--   2. Creates :ArchThemeReload.
--   3. Registers this Neovim instance through an RPC socket.
--   4. Removes the socket when Neovim exits.

-- ============================================================
-- PATHS
-- ============================================================

local config_home = os.getenv("XDG_CONFIG_HOME")

if not config_home or config_home == "" then
	config_home = vim.fn.expand("~/.config")
end

local atm_config = config_home .. "/arch-theme-manager"

local theme_file = atm_config .. "/generated/nvim-theme.lua"

local runtime_root = os.getenv("XDG_RUNTIME_DIR")

if runtime_root and runtime_root ~= "" then
	runtime_root = runtime_root .. "/arch-theme-manager"
else
	local uid = vim.uv.os_getuid()

	runtime_root = "/tmp/arch-theme-manager-" .. tostring(uid)
end

local socket_dir = runtime_root .. "/nvim"

local socket_path = socket_dir .. "/" .. tostring(vim.fn.getpid()) .. ".sock"

-- ============================================================
-- THEME LOADING
-- ============================================================

local function load_theme()
	if vim.fn.filereadable(theme_file) == 0 then
		return false
	end

	local ok, error_message = pcall(dofile, theme_file)

	if not ok then
		vim.schedule(function()
			vim.notify("Arch Theme Manager: " .. tostring(error_message), vim.log.levels.ERROR)
		end)

		return false
	end

	return true
end

-- ============================================================
-- RELOAD COMMAND
-- ============================================================

vim.api.nvim_create_user_command("ArchThemeReload", function()
	load_theme()
end, {
	force = true,
	desc = "Reload Arch Theme Manager theme",
})

-- ============================================================
-- RPC SOCKET
-- ============================================================

vim.fn.mkdir(socket_dir, "p")

-- Remove a stale file with the same PID path if one exists.
if vim.fn.filereadable(socket_path) == 1 then
	pcall(vim.fn.delete, socket_path)
end

local server_ok, server_result = pcall(vim.fn.serverstart, socket_path)

if not server_ok then
	vim.schedule(function()
		vim.notify(
			"Arch Theme Manager: " .. "could not register Neovim socket: " .. tostring(server_result),
			vim.log.levels.WARN
		)
	end)
end

vim.g.arch_theme_manager_socket = socket_path

-- ============================================================
-- CLEANUP
-- ============================================================

vim.api.nvim_create_autocmd("VimLeavePre", {
	once = true,

	callback = function()
		pcall(vim.fn.serverstop, socket_path)

		pcall(vim.fn.delete, socket_path)
	end,
})

-- ============================================================
-- INITIAL LOAD
-- ============================================================

-- Schedule the theme so LazyVim has already completed most of
-- its startup configuration before our generated highlights
-- are applied.
vim.schedule(load_theme)
