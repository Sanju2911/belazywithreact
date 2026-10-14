# Security

This initial release does not promise long-term support. Security fixes should
be applied by upgrading to a maintained release when one is available.

Do not include credentials, tokens, `.env` values, or personal data in public
issues. Private vulnerability reporting is enabled: use GitHub's
**Report a vulnerability** feature under the repository's Security tab.
If that feature becomes unavailable, request a private contact channel without
disclosing exploit details in public.

The CLI downloads and runs create-vite and npm packages from the npm registry.
Review generated package.json and package-lock.json before deployment, and run
`npm audit` to check the generated project's dependencies. The CLI does not
disable npm security checks. All `VITE_` environment variables are exposed to
the browser; never place secrets in them.
