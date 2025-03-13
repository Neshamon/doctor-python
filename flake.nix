{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";
  inputs.nix-github-actions.url = "github:nix-community/nix-github-actions";
  inputs.nix-github-actions.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      nix-github-actions,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      githubActions = nix-github-actions.lib.mkGithubMatrix {
        checks = nixpkgs.lib.getAttrs [ "x86_64-linux" ] self.packages;
      };
      packages.x86_64-linux.hello = nixpkgs.legacyPackages.x86_64-linux.hello;
      packages.x86_64-linux.default = self.packages.x86_64-linux.hello;

      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShell {
            venvDir = ".venv";
            packages =
              with pkgs;
              [
                python313
                sqlite
                basedpyright
              ]
              ++ (with pkgs.python313Packages; [
                pip
                requests
                python-multipart
                jinja2
                sqlmodel
                fastapi
                fastapi-cli
                tailwindcss_4
                pandas
                celery
                venvShellHook
              ]);
          };
        }
      );
    };
}
