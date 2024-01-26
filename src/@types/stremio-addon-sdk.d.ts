declare module "stremio-addon-sdk" {
	export interface Manifest {
		/**
		 * Identifier, dot-separated, e.g. "com.stremio.filmon"
		 */
		id: string;
		/**
		 * Human readable name
		 */
		name: string;
		/**
		 *  Human readable description
		 */
		description: string;
		/**
		 * Semantic version of the addon
		 */
		version: string;
		/**
		 * Supported resources, defined as an array of objects (long version) or strings (short version).
		 *
		 * Example #1: [{"name": "stream", "types": ["movie"], "idPrefixes": ["tt"]}]
		 *
		 * Example #2: ["catalog", "meta", "stream", "subtitles", "addon_catalog"]
		 */
		resources: Array<ShortManifestResource | FullManifestResource>;
		/**
		 * Supported types.
		 */
		types: ContentType[];
		/**
		 * Use this if you want your addon to be called only for specific content IDs.
		 *
		 * For example, if you set this to ["yt_id:", "tt"], your addon will only be called for id values that start with 'yt_id:' or 'tt'.
		 */
		idPrefixes?: string[] | undefined;
		/**
		 * A list of the content catalogs your addon provides.
		 *
		 * Leave this an empty array ([]) if your addon does not provide the catalog resource.
		 */
		catalogs: ManifestCatalog[];
		/**
		 * Array of Catalog objects, a list of other addon manifests.
		 *
		 * This can be used for an addon to act just as a catalog of other addons.
		 */
		addonCatalogs?: ManifestCatalog[] | undefined;

		/**
		 * A list of settings that users can set for your addon.
		 */
		config?: ManifestConfig[];

		/**
		 * Background image for the addon.
		 *
		 * URL to png/jpg, at least 1024x786 resolution.
		 */
		background?: string | undefined;

		/**
		 * @deprecated use `logo` instead.
		 */
		icon?: string;

		/**
		 * Logo icon, URL to png, monochrome, 256x256.
		 */
		logo?: string | undefined;
		/**
		 * Contact email for addon issues.
		 * Used for the Report button in the app.
		 * Also, the Stremio team may reach you on this email for anything relating your addon.
		 */
		contactEmail?: string | undefined;
		behaviorHints?:
			| {
					/**
					 * If the addon includes adult content.
					 *
					 * Defaults to false.
					 */
					adult?: boolean | undefined;
					/**
					 * If the addon includes P2P content, such as BitTorrent, which may reveal the user's IP to other streaming parties.
					 *
					 * Used to provide an adequate warning to the user.
					 */
					p2p?: boolean | undefined;

					/**
					 * Default is `false`. If the addon supports settings, it will add a button next to "Install" in Stremio that will point to the `/configure` path on the addon's domain. For more information, read [User Data](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/api/responses/manifest.md#user-data) (or if you are not using the Addon SDK, read: [Advanced User Data](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/advanced.md#using-user-data-in-addons) and [Creating Addon Configuration Pages](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/advanced.md#creating-addon-configuration-pages))
					 */
					configurable?: boolean;

					/**
					 * Default is `false`. If set to `true`, the "Install" button will not show for your addon in Stremio. Instead a "Configure" button will show pointing to the `/configure` path on the addon's domain. For more information, read [User Data](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/api/responses/manifest.md#user-data) (or if you are not using the Addon SDK, read: [Advanced User Data](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/advanced.md#using-user-data-in-addons) and [Creating Addon Configuration Pages](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/advanced.md#creating-addon-configuration-pages))
					 */
					configurationRequired?: boolean;
			  }
			| undefined;
	}

	export type ManifestConfigType = "text" | "number" | "password" | "checkbox" | "select";

	/**
	 * Addon setting.
	 */
	export interface ManifestConfig {
		/**
		 * A key that will identify the user chosen value.
		 */
		key: string;

		/**
		 * The type of data that the setting stores.
		 */
		type: ManifestConfigType;

		/**
		 * The default value. For `type: "boolean"` this can be set to "checked" to default to enabled.
		 */
		default?: string;

		/**
		 * The title of the setting.
		 */
		title?: string;

		/**
		 * List of (string) choices for `type: "select"`
		 */
		options?: string;

		/**
		 * If the value is required or not. Only applies to the following types: "string", "number". (default is `false`)
		 */
		required?: string;
	}
}
