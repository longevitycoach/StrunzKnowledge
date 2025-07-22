package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

// Configuration
const (
	org         = "longevitycoach"
	packageName = "strunzknowledge"
)

// PackageInfo represents the GitHub package information
type PackageInfo struct {
	Name        string    `json:"name"`
	PackageType string    `json:"package_type"`
	Visibility  string    `json:"visibility"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	HTMLURL     string    `json:"html_url"`
}

// PackageVersion represents a package version
type PackageVersion struct {
	ID        int64     `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	Metadata  struct {
		Container struct {
			Tags []string `json:"tags"`
		} `json:"container"`
	} `json:"metadata"`
}

func main() {
	fmt.Printf("Fetching package information for %s/%s...\n", org, packageName)

	// Check if gh CLI is available
	if err := checkGHCLI(); err != nil {
		log.Fatalf("GitHub CLI not available: %v", err)
	}

	// Get package details
	packageInfo, err := getPackageInfo()
	if err != nil {
		fmt.Println("Package not found or insufficient permissions.")
		fmt.Println("Please ensure your GitHub token has the 'read:packages' scope.")
		os.Exit(1)
	}

	// Display current package info
	displayPackageInfo(packageInfo)

	// Get and display versions
	if err := displayPackageVersions(); err != nil {
		log.Printf("Error getting package versions: %v", err)
	}

	// Display description information
	displayDescriptionInfo()
}

func checkGHCLI() error {
	cmd := exec.Command("gh", "auth", "status")
	return cmd.Run()
}

func getPackageInfo() (*PackageInfo, error) {
	url := fmt.Sprintf("/orgs/%s/packages/container/%s", org, packageName)
	cmd := exec.Command("gh", "api", url)
	
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	var packageInfo PackageInfo
	if err := json.Unmarshal(output, &packageInfo); err != nil {
		return nil, fmt.Errorf("failed to parse package info: %w", err)
	}

	return &packageInfo, nil
}

func displayPackageInfo(info *PackageInfo) {
	fmt.Println("\n📦 Package Information:")
	fmt.Printf("Name: %s\n", info.Name)
	fmt.Printf("Type: %s\n", info.PackageType)
	fmt.Printf("Visibility: %s\n", info.Visibility)
	fmt.Printf("Created: %s\n", info.CreatedAt.Format(time.RFC3339))
	fmt.Printf("Updated: %s\n", info.UpdatedAt.Format(time.RFC3339))
	fmt.Printf("HTML URL: %s\n", info.HTMLURL)
}

func displayPackageVersions() error {
	fmt.Println("\n📋 Package Versions:")
	
	url := fmt.Sprintf("/orgs/%s/packages/container/%s/versions", org, packageName)
	cmd := exec.Command("gh", "api", "--paginate", url)
	
	output, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("failed to get package versions: %w", err)
	}

	var versions []PackageVersion
	if err := json.Unmarshal(output, &versions); err != nil {
		return fmt.Errorf("failed to parse package versions: %w", err)
	}

	// Display up to 20 most recent versions
	count := len(versions)
	if count > 20 {
		count = 20
	}

	for i := 0; i < count; i++ {
		version := versions[i]
		tag := "untagged"
		if len(version.Metadata.Container.Tags) > 0 {
			tag = version.Metadata.Container.Tags[0]
		}
		
		fmt.Printf("  - %s (ID: %d, Created: %s)\n", 
			tag, version.ID, version.CreatedAt.Format(time.RFC3339))
	}

	fmt.Println("\n(Showing up to 20 most recent versions)")
	return nil
}

func displayDescriptionInfo() {
	fmt.Println("\n📝 Package Description:")
	fmt.Println("Note: GitHub Container Registry packages don't have editable descriptions via API.")
	fmt.Println("Descriptions are typically set through:")
	fmt.Println("  1. The Dockerfile LABEL org.opencontainers.image.description")
	fmt.Println("  2. Repository README that's linked to the package")
	fmt.Println("  3. GitHub Actions workflow annotations")

	fmt.Println("\nTo add descriptions to your Docker images, update your Dockerfile:")
	fmt.Println("  LABEL org.opencontainers.image.description=\"Dr. Strunz Knowledge Base MCP Server\"")
	fmt.Println("  LABEL org.opencontainers.image.source=\"https://github.com/longevitycoach/StrunzKnowledge\"")
	fmt.Println("  LABEL org.opencontainers.image.authors=\"longevitycoach\"")
	fmt.Println("  LABEL org.opencontainers.image.title=\"StrunzKnowledge MCP Server\"")
}
