
import api from './api';

const WORKSPACE_ID = 'default-workspace';

function getList(data, keys = []) {
  if (Array.isArray(data)) return data;

  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }

  return [];
}

function getRoadmapId(roadmap) {
  return roadmap?.roadmap_id || roadmap?.id || roadmap?._id || null;
}

export const executiveSummaryService = {
  async getCurrentSummary() {
    const roadmapResponse = await api.get('/roadmaps', {
      params: {
        workspace_id: WORKSPACE_ID,
        limit: 50,
      },
    });

    const roadmaps = getList(roadmapResponse.data, [
      'roadmaps',
      'items',
    ]);

    const roadmap =
      roadmaps.find(
        (item) =>
          item.roadmap_type === 'baseline' &&
          item.is_current !== false
      ) ||
      roadmaps.find((item) => item.is_current !== false) ||
      null;

    if (!roadmap) {
      return {
        roadmap: null,
        summary: null,
      };
    }

    const roadmapId = getRoadmapId(roadmap);

    if (!roadmapId) {
      throw new Error(
        'The current roadmap does not contain a valid roadmap ID.'
      );
    }

    const summaryResponse = await api.get('/executive-summaries', {
      params: {
        workspace_id: WORKSPACE_ID,
        roadmap_id: roadmapId,
        current_only: true,
      },
    });

    const summaries = getList(summaryResponse.data, [
      'summaries',
      'items',
    ]);

    const summary =
      summaries.find((item) => item.is_current !== false) ||
      summaries[0] ||
      null;

    return {
      roadmap,
      summary,
    };
  },

  async generateSummary(roadmapId) {
    if (!roadmapId) {
      throw new Error(
        'No current roadmap is available. Generate or save a roadmap first.'
      );
    }

    const response = await api.post(
      '/executive-summaries/generate',
      {
        workspace_id: WORKSPACE_ID,
        roadmap_id: roadmapId,
      }
    );

    return response.data;
  },
};
