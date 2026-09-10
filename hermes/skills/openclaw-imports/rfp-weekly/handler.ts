import { SkillContext, SkillResult } from "openclaw/skill-sdk";

/**
 * RFP Weekly Brief Skill Handler
 * Fetches government RFPs and delivers via Telegram
 */

export async function handler(ctx: SkillContext): Promise<SkillResult> {
  const action = ctx.params?.action || "fetch";
  const samApiKey = process.env.SAM_API_KEY;

  if (!samApiKey) {
    return {
      status: "error",
      message: "SAM_API_KEY environment variable not set. See SKILL.md for setup.",
      output: "",
    };
  }

  if (action === "fetch") {
    return await fetchAndDigest(ctx, samApiKey);
  }

  return {
    status: "error",
    message: `Unknown action: ${action}. Supported: fetch`,
    output: "",
  };
}

async function fetchAndDigest(
  ctx: SkillContext,
  samApiKey: string
): Promise<SkillResult> {
  try {
    ctx.log("info", "Starting SAM.gov RFP fetch...");

    const opportunities = await fetchSamGov(samApiKey);
    
    if (opportunities.length === 0) {
      return {
        status: "ok",
        message: "No opportunities found in SAM.gov this week.",
        output: "No new RFPs found.",
      };
    }

    const digest = formatTelegramDigest(opportunities);
    
    ctx.log("info", `Found ${opportunities.length} opportunities, formatted digest`);

    return {
      status: "ok",
      message: `Fetched ${opportunities.length} opportunities from SAM.gov`,
      output: digest,
      deliveryHint: {
        channel: "telegram",
        format: "markdown",
      },
    };
  } catch (error) {
    ctx.log("error", `RFP fetch failed: ${String(error)}`);
    return {
      status: "error",
      message: `Failed to fetch RFPs: ${String(error)}`,
      output: "",
    };
  }
}

async function fetchSamGov(apiKey: string): Promise<Array<Record<string, any>>> {
  const keywords = ["video", "production", "media", "film", "animation", "explainer"];
  const params = new URLSearchParams({
    api_key: apiKey,
    keyword: keywords.join(" OR "),
    sort: "-postedDate",
    limit: "10",
  });

  const url = `https://api.sam.gov/opportunities/v1/search?${params}`;

  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "Rival Productions RFP Bot/1.0",
      },
      timeout: 15000,
    });

    if (!response.ok) {
      throw new Error(`SAM.gov API returned ${response.status}`);
    }

    const data = await response.json() as Record<string, any>;
    const opps = data.opportunitiesData || [];

    return opps.map((opp: Record<string, any>) => ({
      notice_id: opp.noticeId,
      title: opp.title,
      agency: opp.agencyName,
      location: Array.isArray(opp.placeOfPerformanceState)
        ? opp.placeOfPerformanceState[0]
        : "National",
      posted: opp.postedDate,
      due: opp.responseDeadline || "",
      naics: opp.naicscode || "",
      setaside: opp.setaside || "",
      link: `https://sam.gov/opp/${opp.noticeId}`,
      scope: (opp.description || "").substring(0, 300),
      fit_score: scoreOpportunity(opp),
    }));
  } catch (error) {
    throw new Error(`SAM.gov fetch failed: ${String(error)}`);
  }
}

function scoreOpportunity(opp: Record<string, any>): number {
  let score = 0;
  const text = `${opp.title} ${opp.description} ${opp.agencyName}`.toLowerCase();

  const keywords = ["video", "production", "media", "film", "animation", "explainer", "creative", "content"];
  keywords.forEach((kw) => {
    if (text.includes(kw)) score += 10;
  });

  const priorityStates = ["PA", "NJ", "DE"];
  const location = String(opp.placeOfPerformanceState || "");
  priorityStates.forEach((state) => {
    if (location.includes(state)) score += 25;
  });

  if (opp.responseDeadline) score += 5;

  return Math.min(score, 100);
}

function formatTelegramDigest(opps: Array<Record<string, any>>): string {
  const lines: string[] = [];
  lines.push("📋 *Rival Productions Weekly RFP Brief*");
  lines.push(`📅 ${new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}`);
  lines.push("🔍 Source: SAM.gov (Federal Opportunities)");
  lines.push("");

  lines.push(`*Top ${Math.min(opps.length, 5)} Opportunities:*`);
  lines.push("");

  opps.slice(0, 5).forEach((opp, i) => {
    lines.push(`*${i + 1}. ${opp.title.substring(0, 60)}*`);
    lines.push(`🏛️ ${opp.agency}`);
    lines.push(`📍 ${opp.location}`);

    if (opp.due) {
      lines.push(`⏰ Due: ${opp.due.substring(0, 10)}`);
    }

    if (opp.fit_score) {
      const fit = opp.fit_score;
      const filled = Math.floor(fit / 20);
      const empty = 5 - filled;
      const bar = "🟢".repeat(filled) + "⚪".repeat(empty);
      lines.push(`Fit: ${bar} ${fit}/100`);
    }

    lines.push(`🔗 ${opp.link}`);
    lines.push("");
  });

  lines.push("---");
  lines.push("💡 *Tip:* Check deadlines before bidding. Full details available at link.");

  return lines.join("\n");
}
