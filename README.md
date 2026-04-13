# Rudder hub

A curated collection of ready-to-use Rudder resources, reviewed by the Rudder team and shared with the entire Rudder ecosystem.
In this first iteration, this repository only contains Techniques, but more resources like scripts and tools will be added in the future.

## What are techniques?

Techniques are the building blocks of configuration management in Rudder. They define how systems should be configured, hardened, and audited. Every Rudder user writes techniques tailored to their infrastructure — but many needs are shared across organizations.

This repository exists to bridge that gap.

## Why this library?

Today, every Rudder user builds their techniques from scratch. There is no standardized way to share proven, battle-tested configurations across the ecosystem. This means duplicated effort, reinvented wheels, and missed opportunities.

The Rudder Hub aims to change that by providing:

- **Ready-to-use techniques** that save time on common use cases
- **A review process** ensuring quality and consistency before anything is published
- **A central place** where anyone — customer or not — can find and contribute techniques

## How it's organized

In the `techniques` folder, each techniques are organized by category:

```
techniques/
├── hardening/
├── audit/
├── compliance/
└── ...
```

Each technique lives in its own directory within the appropriate category and includes the technique file and potential resources.

## Using a technique

1. Browse the categories and find a technique that fits your needs
2. Read the technique documentation to understand what it does and any prerequisites
3. Import it into your Rudder instance
4. **Test it in a non-production environment first**
5. Adapt it to your specific context if needed

## Contributing

We welcome contributions from all Rudder users. The contribution process is currently being defined — stay tuned for detailed guidelines.

In the meantime, if you have a technique you'd like to share, feel free to open an issue to start the conversation.

## Review process

All submitted techniques are reviewed by the Rudder Customer Services team before being published. This review checks for quality, consistency, and adherence to best practices.

## Disclaimer

All techniques in this library are provided **as-is, without warranty of any kind**. While every submission is reviewed by the Rudder team, this does not constitute a guarantee that a technique will work in your specific environment or will not cause unintended side effects.

**You are responsible for testing any technique in your own environment before deploying it to production.** Rudder cannot be held liable for any damage resulting from the use of content provided in this repository.

## License

All content in this repository is licensed under the [GNU General Public License v3.0](LICENSE) (GPLv3), consistent with the Rudder project.

By contributing to this repository, you agree to license your contributions under the same terms.
